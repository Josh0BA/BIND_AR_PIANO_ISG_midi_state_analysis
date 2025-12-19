import os
import pandas as pd
import numpy as np
from scipy.stats import shapiro
import statsmodels.api as sm
import statsmodels.formula.api as smf

from midi_state_analysis.folder_utils import find_midi_data_folder


def locate_transition_csv(explicit_path: str | None = None) -> str:
    """Locate the CSV produced by midi_state_analysis (MIDI_ANALYSIS_STATES.csv)."""
    candidates = []
    if explicit_path:
        candidates.append(explicit_path)

    midi_folder = find_midi_data_folder(start_path='.')
    if midi_folder:
        candidates.append(os.path.join(os.path.dirname(midi_folder), "MIDI_ANALYSIS_STATES.csv"))

    candidates.append(os.path.join(os.getcwd(), "MIDI_ANALYSIS_STATES.csv"))

    for path in candidates:
        if path and os.path.isfile(path):
            return path

    raise FileNotFoundError("Keine CSV-Datei mit Transitionen gefunden. Führe zuerst midi-analysis aus.")


def classify_block(block: str) -> str:
    b = str(block).lower()
    if "pre" in b or "post" in b or "test" in b:
        return "Test"
    if b.startswith("b"):
        return "Training"
    return "Unbekannt"


def prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["transition_time_s"] = pd.to_numeric(df["transition_time_s"], errors="coerce")
    df["block_type"] = df["block"].apply(classify_block)
    if "state_from_freq" not in df.columns:
        df["state_from_freq"] = "UNKNOWN"
    return df.dropna(subset=["transition_time_s"])


def summarize(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    rows = []
    for keys, group in df.groupby(group_cols):
        series = group["transition_time_s"].dropna()
        keys_tuple = keys if isinstance(keys, tuple) else (keys,)
        row = {col: val for col, val in zip(group_cols, keys_tuple)}
        row.update({
            "n": len(series),
            "mean_s": series.mean(),
            "std_s": series.std(ddof=1),
            "median_s": series.median(),
        })
        rows.append(row)
    return pd.DataFrame(rows).sort_values(group_cols)


def shapiro_by_group(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    rows = []
    for name, group in df.groupby(group_col):
        series = group["transition_time_s"].dropna()
        if len(series) < 3:
            w_stat, p_val = (np.nan, np.nan)
        else:
            w_stat, p_val = shapiro(series)
        rows.append({
            group_col: name,
            "n": len(series),
            "shapiro_W": w_stat,
            "shapiro_p": p_val,
            "normal": p_val >= 0.05 if not np.isnan(p_val) else False,
        })
    return pd.DataFrame(rows).sort_values(group_col)


def run_anova(df: pd.DataFrame) -> pd.DataFrame:
    # Two-way ANOVA: block_type and transition_id; interaction included.
    model = smf.ols(
        "transition_time_s ~ C(block_type) + C(transition_id) + C(block_type):C(transition_id)",
        data=df,
    ).fit()
    return sm.stats.anova_lm(model, typ=2)


def run_oneway_anova_by_transition(df: pd.DataFrame) -> pd.DataFrame:
    # One-way ANOVA: transition_id within a subset (e.g., a single block)
    if df["transition_id"].nunique() < 2:
        raise ValueError("Zu wenige unterschiedliche transition_id für ANOVA.")
    model = smf.ols("transition_time_s ~ C(transition_id)", data=df).fit()
    return sm.stats.anova_lm(model, typ=2)


def anova_per_block(df: pd.DataFrame) -> list[tuple[str, pd.DataFrame]]:
    results = []
    for blk in sorted(df["block"].unique()):
        subset = df[df["block"] == blk]
        try:
            table = run_oneway_anova_by_transition(subset)
            results.append((f"ANOVA für Block {blk}", table))
        except Exception as exc:
            results.append((f"ANOVA für Block {blk}", pd.DataFrame({"Hinweis": [str(exc)]})))
    return results


def print_section(title: str, content: pd.DataFrame) -> None:
    print(f"\n=== {title} ===")
    if content.empty:
        print("Keine Daten.")
    else:
        print(content.to_string(index=False))


def main(csv_path: str | None = None) -> None:
    path = locate_transition_csv(csv_path)
    print(f"✓ Lade Transitionen aus: {path}")
    df = pd.read_csv(path)
    if df.empty:
        print("CSV ist leer.")
        return

    required = {"transition_id", "transition_time_s", "block"}
    missing = required - set(df.columns)
    if missing:
        print(f"Fehlende Spalten in der CSV: {', '.join(sorted(missing))}")
        return

    df = prepare_dataframe(df)

    print_section("Grundlegende Kennzahlen je Transition", summarize(df, ["transition_id"]))
    print_section("Kennzahlen nach Block-Typ (Test/Training)", summarize(df, ["block_type", "transition_id"]))
    print_section("Kennzahlen nach Frequenz (h/s)", summarize(df, ["state_from_freq", "transition_id"]))
    print_section("Shapiro je Transition", shapiro_by_group(df, "transition_id"))

    try:
        anova_table = run_anova(df)
        print_section("ANOVA (block_type, transition_id, Interaktion)", anova_table)
    except Exception as exc:
        print(f"ANOVA konnte nicht berechnet werden: {exc}")

    # One-way ANOVAs pro Block (inkl. Pre-/Posttest, falls als Block benannt)
    for title, table in anova_per_block(df):
        print_section(title, table)


if __name__ == "__main__":
    main()