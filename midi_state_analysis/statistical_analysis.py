import os
import pandas as pd
import numpy as np
from scipy.stats import t, shapiro

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


def ci_bounds(series: pd.Series, confidence: float = 0.95) -> tuple[float, float]:
    n = len(series)
    if n < 2:
        return (np.nan, np.nan)
    se = series.std(ddof=1) / np.sqrt(n)
    t_crit = t.ppf(1 - (1 - confidence) / 2, n - 1)
    delta = t_crit * se
    mean_val = series.mean()
    return (mean_val - delta, mean_val + delta)


def summarize_transition_times(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    rows = []
    for keys, group in df.groupby(group_cols):
        series = group["transition_time_s"].dropna()
        ci_low, ci_up = ci_bounds(series)
        keys_tuple = keys if isinstance(keys, tuple) else (keys,)
        row = {col: val for col, val in zip(group_cols, keys_tuple)}
        row.update({
            "n": len(series),
            "mean_s": series.mean(),
            "std_s": series.std(ddof=1),
            "median_s": series.median(),
            "min_s": series.min(),
            "max_s": series.max(),
            "ci_lower_s": ci_low,
            "ci_upper_s": ci_up,
        })
        rows.append(row)
    return pd.DataFrame(rows).sort_values(group_cols)


def normality_by_transition(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for tid, group in df.groupby("transition_id"):
        series = group["transition_time_s"].dropna()
        if len(series) < 3:
            w_stat, p_val = (np.nan, np.nan)
        else:
            w_stat, p_val = shapiro(series)
        rows.append({
            "transition_id": tid,
            "n": len(series),
            "shapiro_W": w_stat,
            "shapiro_p": p_val,
            "normal": p_val >= 0.05 if not np.isnan(p_val) else False,
        })
    return pd.DataFrame(rows).sort_values("transition_id")


def print_section(title: str, df: pd.DataFrame) -> None:
    print(f"\n=== {title} ===")
    if df.empty:
        print("Keine Daten.")
        return
    print(df.to_string(index=False))


def prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["block_type"] = df["block"].apply(classify_block)
    df["transition_time_s"] = pd.to_numeric(df["transition_time_s"], errors="coerce")
    return df.dropna(subset=["transition_time_s"])


def main(csv_path: str | None = None) -> None:
    path = locate_transition_csv(csv_path)
    print(f"✓ Lade Transitionen aus: {path}")
    df = pd.read_csv(path)
    if df.empty:
        print("CSV ist leer.")
        return

    df = prepare_dataframe(df)

    overall = summarize_transition_times(df, ["transition_id"])
    by_block_type = summarize_transition_times(df, ["block_type", "transition_id"])
    by_block = summarize_transition_times(df, ["block", "transition_id"])
    by_freq = summarize_transition_times(df, ["state_from_freq", "transition_id"])
    normality = normality_by_transition(df)

    print_section("Übersicht je Übergangscode", overall)
    print_section("Übersicht je Block-Typ (Test/Training)", by_block_type)
    print_section("Übersicht je Block", by_block)
    print_section("Übersicht je Frequenz (h/s)", by_freq)
    print_section("Normalitätscheck (Shapiro)", normality)


if __name__ == "__main__":
    main()




