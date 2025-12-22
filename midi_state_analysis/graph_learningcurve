"""
Creates ONE learning-curve plot (transition time) with 3 curves:
- all together (all)
- frequent (h)
- rare (s)
"""

from __future__ import annotations
import os
import pandas as pd
import matplotlib.pyplot as plt


# =========================
# CONFIG
# =========================
CSV_PATH = "MIDI_ANALYSIS_STATES_ALL.csv" # ("Daten (MIDI).csv")

COL_BLOCK = "block"
COL_GROUP = "group"              # not plotted anymore, but kept for compatibility
COL_FREQ  = "freq"               # 'h' / 's'
COL_TT    = "transition_time_s"

BLOCK_ORDER = ["pretest", "b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8", "posttest"]

OUT_DIR = "plots"
os.makedirs(OUT_DIR, exist_ok=True)


def _prep(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df[COL_BLOCK] = df[COL_BLOCK].astype(str).str.strip().str.lower()
    df[COL_FREQ]  = df[COL_FREQ].astype(str).str.strip().str.lower()
    df[COL_TT]    = pd.to_numeric(df[COL_TT], errors="coerce")

    df = df.dropna(subset=[COL_BLOCK, COL_FREQ, COL_TT])
    df = df[df[COL_BLOCK].isin(BLOCK_ORDER)]

    df[COL_BLOCK] = pd.Categorical(
        df[COL_BLOCK],
        categories=BLOCK_ORDER,
        ordered=True
    )
    return df


def compute_means(df: pd.DataFrame, label: str) -> pd.DataFrame:
    means = (
        df.groupby(COL_BLOCK, observed=True)[COL_TT]
          .mean()
          .reset_index()
          .rename(columns={COL_TT: "mean_tt"})
    )
    means["label"] = label
    return means


def plot_learning_curve_combined(means: pd.DataFrame, title: str, out_path: str) -> None:
    plt.figure(figsize=(12, 5))

    for lbl in means["label"].unique():
        sub = means[means["label"] == lbl].sort_values(COL_BLOCK)
        plt.plot(
            sub[COL_BLOCK].astype(str),
            sub["mean_tt"],
            linewidth=2,
            label=lbl
        )

    plt.title(title)
    plt.xlabel("")
    plt.ylabel("Transition time (s)")
    plt.grid(True, axis="y", alpha=0.3)
    plt.legend(loc="center left", bbox_to_anchor=(1.02, 0.5))
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close()


def main() -> None:
    df = pd.read_csv(CSV_PATH)
    df = _prep(df)

    means_all = compute_means(df, "all")
    means_h   = compute_means(df[df[COL_FREQ] == "h"], "frequent (h)")
    means_s   = compute_means(df[df[COL_FREQ] == "s"], "rare (s)")

    means = pd.concat([means_all, means_h, means_s], ignore_index=True)

    plot_learning_curve_combined(
        means,
        "Learning curve during the acquisition phase",
        os.path.join(OUT_DIR, "learning_curve_all_h_s.png")
    )

    print("Done. Saved plot to:", OUT_DIR)


if __name__ == "__main__":
    main()
