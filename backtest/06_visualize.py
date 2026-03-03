"""
06_visualize.py — Generate 6 backtest charts.

Input:  output/seasons_ground_truth.csv
        output/altcoin_market_returns.parquet
        output/bm_signals.parquet
        output/ethroc_signals.parquet
        output/backtest_results.csv

Output: charts/01_ground_truth_seasons.png
        charts/02_bm_method_comparison.png
        charts/03_ethroc_method_comparison.png
        charts/04_lead_time_boxplot.png
        charts/05_noise_comparison.png
        charts/06_combined_score_heatmap.png
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

from config import (
    OUTPUT_DIR, CHARTS_DIR,
    CHART_THEME, CHART_FIGSIZE, CHART_DPI,
    SEASON_THRESHOLD,
    BM14_ENTRY, BM14_EXIT, BM30_ENTRY, BM30_EXIT,
)

plt.style.use(CHART_THEME)


def load_data():
    """Load all output data files."""
    seasons = pd.read_csv(os.path.join(OUTPUT_DIR, "seasons_ground_truth.csv"))
    seasons["start_date"] = pd.to_datetime(seasons["start_date"])
    seasons["peak_date"] = pd.to_datetime(seasons["peak_date"])
    seasons["end_date"] = pd.to_datetime(seasons["end_date"])

    returns_df = pd.read_parquet(os.path.join(OUTPUT_DIR, "altcoin_market_returns.parquet"))
    returns_df.index = pd.to_datetime(returns_df.index)

    bm_signals = pd.read_parquet(os.path.join(OUTPUT_DIR, "bm_signals.parquet"))
    bm_signals.index = pd.to_datetime(bm_signals.index)

    ethroc_signals = pd.read_parquet(os.path.join(OUTPUT_DIR, "ethroc_signals.parquet"))
    ethroc_signals.index = pd.to_datetime(ethroc_signals.index)

    combined = pd.read_csv(os.path.join(OUTPUT_DIR, "backtest_results.csv"))

    return seasons, returns_df, bm_signals, ethroc_signals, combined


def add_season_shading(ax, seasons, alpha=0.15):
    """Add green shading for season periods."""
    for _, s in seasons.iterrows():
        ax.axvspan(s["start_date"], s["end_date"],
                   color="#00e676", alpha=alpha, zorder=0)


# ── Chart 1: Ground Truth Seasons ─────────────────────────────────────

def chart_ground_truth(seasons, returns_df):
    """Altcoin outperformance vs BTC with season shading and peak markers."""
    fig, ax = plt.subplots(figsize=CHART_FIGSIZE)

    outperf = returns_df["outperformance"]
    ax.plot(outperf.index, outperf.values, color="#00bcd4", linewidth=0.8, alpha=0.8)
    ax.fill_between(outperf.index, 0, outperf.values,
                    where=outperf > 0, color="#00bcd4", alpha=0.1)

    # Season shading
    add_season_shading(ax, seasons, alpha=0.2)

    # Peak markers
    for _, s in seasons.iterrows():
        ax.axvline(s["peak_date"], color="#f44336", linewidth=1.5, alpha=0.7, linestyle="--")
        ax.plot(s["peak_date"], outperf.loc[:s["peak_date"]].iloc[-1] if s["peak_date"] in outperf.index else 0,
                "o", color="#f44336", markersize=8, zorder=5)

    # Threshold line
    ax.axhline(SEASON_THRESHOLD, color="#00e676", linewidth=1, linestyle="--", alpha=0.5)
    ax.text(outperf.index[10], SEASON_THRESHOLD + 1, f"+{SEASON_THRESHOLD}% threshold",
            color="#00e676", fontsize=8, alpha=0.7)
    ax.axhline(0, color="white", linewidth=0.5, alpha=0.3)

    ax.set_title("Altcoin Season Ground Truth (2019–2024)", fontsize=14, fontweight="bold")
    ax.set_ylabel("Altcoin Outperformance vs BTC (%)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    fig.autofmt_xdate()

    path = os.path.join(CHARTS_DIR, "01_ground_truth_seasons.png")
    fig.tight_layout()
    fig.savefig(path, dpi=CHART_DPI)
    plt.close(fig)
    print(f"  Saved: {path}")


# ── Chart 2: BM Method Comparison ─────────────────────────────────────

def chart_bm_comparison(seasons, bm_signals):
    """3 subplots: BM14, BM30, EMA crossover — with entry/exit dots."""
    fig, axes = plt.subplots(3, 1, figsize=(CHART_FIGSIZE[0], 12), sharex=True)

    methods = [
        ("bm14", "bm14_signal", "BM_14D", BM14_ENTRY, BM14_EXIT),
        ("bm30", "bm30_signal", "BM_30D", BM30_ENTRY, BM30_EXIT),
        ("ema_cross", "ema_signal", "EMA Crossover (7/21)", None, None),
    ]

    for ax, (val_col, sig_col, title, entry_th, exit_th) in zip(axes, methods):
        vals = bm_signals[val_col].dropna()
        ax.plot(vals.index, vals.values, color="#00e676", linewidth=1, alpha=0.8)

        # Season shading
        add_season_shading(ax, seasons)

        # Entry/Exit dots
        entries = bm_signals[bm_signals[sig_col] == "ENTRY"]
        exits = bm_signals[bm_signals[sig_col] == "EXIT"]
        if len(entries) > 0:
            ax.scatter(entries.index, bm_signals.loc[entries.index, val_col],
                       color="#00e676", s=40, zorder=5, label="ENTRY")
        if len(exits) > 0:
            ax.scatter(exits.index, bm_signals.loc[exits.index, val_col],
                       color="#f44336", s=40, zorder=5, label="EXIT", marker="v")

        # Threshold lines
        if entry_th is not None:
            ax.axhline(entry_th, color="#00e676", linewidth=0.8, linestyle="--", alpha=0.4)
            ax.axhline(exit_th, color="#f44336", linewidth=0.8, linestyle="--", alpha=0.4)
        ax.axhline(0, color="white", linewidth=0.5, alpha=0.3)

        ax.set_title(title, fontsize=11, fontweight="bold")
        ax.set_ylabel("BM Value")
        ax.legend(loc="upper right", fontsize=8)

    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    axes[-1].xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    fig.autofmt_xdate()

    fig.suptitle("BM Signal Methods Comparison", fontsize=14, fontweight="bold", y=1.01)
    path = os.path.join(CHARTS_DIR, "02_bm_method_comparison.png")
    fig.tight_layout()
    fig.savefig(path, dpi=CHART_DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


# ── Chart 3: ETH/BTC ROC Method Comparison ────────────────────────────

def chart_ethroc_comparison(seasons, ethroc_signals):
    """3 subplots: ROC7, ROC14, ROC7+3D confirm — with peak warning dots."""
    fig, axes = plt.subplots(3, 1, figsize=(CHART_FIGSIZE[0], 12), sharex=True)

    methods = [
        ("roc7", "roc7_peak_warning", "ROC_7D"),
        ("roc14", "roc14_peak_warning", "ROC_14D"),
        ("roc7c", "roc7c_peak_warning", "ROC_7D + 3-Day Confirm"),
    ]

    for ax, (val_col, warn_col, title) in zip(axes, methods):
        vals = ethroc_signals[val_col].dropna()
        ax.plot(vals.index, vals.values, color="#00bcd4", linewidth=1, alpha=0.8)

        # Season shading
        add_season_shading(ax, seasons)

        # Peak warning dots
        warnings = ethroc_signals[ethroc_signals[warn_col] == True]
        if len(warnings) > 0:
            ax.scatter(warnings.index, ethroc_signals.loc[warnings.index, val_col],
                       color="#ff9800", s=50, zorder=5, label="Peak Warning", marker="D")

        # Peak ground truth markers
        for _, s in seasons.iterrows():
            ax.axvline(s["peak_date"], color="#f44336", linewidth=1, alpha=0.5, linestyle=":")

        # Reference lines
        ax.axhline(3, color="#00e676", linewidth=0.8, linestyle="--", alpha=0.4)
        ax.axhline(0, color="white", linewidth=0.5, alpha=0.3)
        ax.axhline(-3, color="#ff9800", linewidth=0.8, linestyle="--", alpha=0.4)

        ax.set_title(title, fontsize=11, fontweight="bold")
        ax.set_ylabel("ETH/BTC ROC (%)")
        ax.legend(loc="upper right", fontsize=8)

    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    axes[-1].xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    fig.autofmt_xdate()

    fig.suptitle("ETH/BTC ROC Peak Warning Methods", fontsize=14, fontweight="bold", y=1.01)
    path = os.path.join(CHARTS_DIR, "03_ethroc_method_comparison.png")
    fig.tight_layout()
    fig.savefig(path, dpi=CHART_DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


# ── Chart 4: Lead Time Boxplot ────────────────────────────────────────

def chart_lead_time_boxplot(seasons, bm_signals, ethroc_signals):
    """Boxplot of lead time (days before season/peak) by method."""
    from backtest_05 import test_bm_lead_time, test_ethroc_lead_time

    # This function is called from main() which handles imports differently.
    # We re-run the tests inline to get lead time data.
    pass


def chart_lead_time_boxplot_from_data(bm_lead_df, roc_lead_df):
    """Boxplot from pre-computed lead time data."""
    fig, ax = plt.subplots(figsize=CHART_FIGSIZE)

    all_data = []
    labels = []
    colors = []

    for method, label in [("bm14", "BM_14D"), ("bm30", "BM_30D"), ("ema", "EMA")]:
        leads = bm_lead_df[bm_lead_df["method"] == method]["lead_days"].dropna().values
        all_data.append(leads)
        labels.append(label)
        med = np.median(leads) if len(leads) > 0 else 0
        colors.append("#00e676" if med > 0 else "#f44336")

    for method, label in [("roc7", "ROC_7D"), ("roc14", "ROC_14D"), ("roc7c", "ROC_7D+3D")]:
        leads = roc_lead_df[roc_lead_df["method"] == method]["lead_days"].dropna().values
        all_data.append(leads)
        labels.append(label)
        med = np.median(leads) if len(leads) > 0 else 0
        colors.append("#00e676" if med > 0 else "#f44336")

    bp = ax.boxplot(all_data, labels=labels, patch_artist=True, widths=0.5)
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color + "30")
        patch.set_edgecolor(color)
    for whisker in bp["whiskers"]:
        whisker.set_color("white")
        whisker.set_alpha(0.5)
    for cap in bp["caps"]:
        cap.set_color("white")
        cap.set_alpha(0.5)
    for median_line in bp["medians"]:
        median_line.set_color("white")
        median_line.set_linewidth(2)

    ax.axhline(0, color="#ff9800", linewidth=1, linestyle="--", alpha=0.5)
    ax.text(0.5, 1, "Break-even (0 days)", color="#ff9800", fontsize=8, alpha=0.7)

    ax.set_title("Lead Time by Method (days before season/peak)", fontsize=14, fontweight="bold")
    ax.set_ylabel("Lead Days (positive = early)")
    ax.tick_params(axis="x", rotation=30)

    path = os.path.join(CHARTS_DIR, "04_lead_time_boxplot.png")
    fig.tight_layout()
    fig.savefig(path, dpi=CHART_DPI)
    plt.close(fig)
    print(f"  Saved: {path}")


# ── Chart 5: Noise Comparison ─────────────────────────────────────────

def chart_noise_comparison(bm_false_df, roc_false_df):
    """Bar chart of signals/warnings per year by method."""
    fig, ax = plt.subplots(figsize=CHART_FIGSIZE)

    methods = []
    values = []
    bar_colors = []

    for method, label in [("bm14", "BM_14D"), ("bm30", "BM_30D"), ("ema", "EMA")]:
        if method in bm_false_df.index:
            v = bm_false_df.loc[method, "signals_per_year"]
            methods.append(label)
            values.append(v)
            bar_colors.append("#00e676" if v < 10 else "#ff9800" if v < 15 else "#f44336")

    for method, label in [("roc7", "ROC_7D"), ("roc14", "ROC_14D"), ("roc7c", "ROC_7D+3D")]:
        if method in roc_false_df.index:
            v = roc_false_df.loc[method, "warnings_per_year"]
            methods.append(label)
            values.append(v)
            bar_colors.append("#00e676" if v < 8 else "#ff9800" if v < 12 else "#f44336")

    bars = ax.bar(methods, values, color=bar_colors, alpha=0.8, edgecolor="white", linewidth=0.5)

    # Value labels on bars
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                f"{val:.1f}", ha="center", va="bottom", fontsize=10, color="white")

    ax.axhline(10, color="#ff9800", linewidth=1, linestyle="--", alpha=0.5)
    ax.text(len(methods) - 0.5, 10.5, "Target max (10/yr)", color="#ff9800", fontsize=8, alpha=0.7)

    ax.set_title("Signals per Year by Method", fontsize=14, fontweight="bold")
    ax.set_ylabel("Signals / Year")
    ax.tick_params(axis="x", rotation=30)

    path = os.path.join(CHARTS_DIR, "05_noise_comparison.png")
    fig.tight_layout()
    fig.savefig(path, dpi=CHART_DPI)
    plt.close(fig)
    print(f"  Saved: {path}")


# ── Chart 6: Combined Score Heatmap ───────────────────────────────────

def chart_combined_heatmap(combined_df):
    """3x3 heatmap of combined scores: BM method × ETH ROC method."""
    fig, ax = plt.subplots(figsize=(10, 7))

    # Pivot to 3×3 matrix
    bm_methods = ["bm14", "bm30", "ema"]
    roc_methods = ["roc7", "roc14", "roc7c"]
    bm_labels = ["BM_14D", "BM_30D", "EMA"]
    roc_labels = ["ROC_7D", "ROC_14D", "ROC_7D+3D"]

    matrix = np.zeros((3, 3))
    for i, bm in enumerate(bm_methods):
        for j, roc in enumerate(roc_methods):
            row = combined_df[
                (combined_df["bm_method"] == bm) &
                (combined_df["roc_method"] == roc)
            ]
            if len(row) > 0:
                matrix[i, j] = row.iloc[0]["combined_score"]

    im = ax.imshow(matrix, cmap="RdYlGn", aspect="auto", vmin=matrix.min() - 5, vmax=matrix.max() + 5)

    # Labels
    ax.set_xticks(range(3))
    ax.set_xticklabels(roc_labels, fontsize=11)
    ax.set_yticks(range(3))
    ax.set_yticklabels(bm_labels, fontsize=11)
    ax.set_xlabel("ETH/BTC ROC Method", fontsize=12)
    ax.set_ylabel("BM Method", fontsize=12)

    # Annotate cells
    best_idx = np.unravel_index(matrix.argmax(), matrix.shape)
    for i in range(3):
        for j in range(3):
            val = matrix[i, j]
            is_best = (i, j) == best_idx
            color = "black" if val > (matrix.min() + matrix.max()) / 2 else "white"
            weight = "bold" if is_best else "normal"
            text = f"{val:.1f}"
            if is_best:
                text += "\n★ BEST"
            ax.text(j, i, text, ha="center", va="center",
                    fontsize=12 if is_best else 10, color=color, fontweight=weight)

    fig.colorbar(im, ax=ax, label="Combined Score", shrink=0.8)
    ax.set_title("Combined Score: BM Method × ETH ROC Method",
                 fontsize=14, fontweight="bold", pad=15)

    path = os.path.join(CHARTS_DIR, "06_combined_score_heatmap.png")
    fig.tight_layout()
    fig.savefig(path, dpi=CHART_DPI)
    plt.close(fig)
    print(f"  Saved: {path}")


# ── Main ──────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("ABM BACKTEST — Step 6: Visualization")
    print("=" * 60)

    seasons, returns_df, bm_signals, ethroc_signals, combined = load_data()
    print(f"Loaded: {len(seasons)} seasons, {len(bm_signals)} BM days, "
          f"{len(ethroc_signals)} ETH ROC days")

    # We need lead time data for charts 4-5, so re-run the relevant tests
    import importlib
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    # Import test functions from 05_test_runner
    from importlib import import_module
    test_runner = import_module("05_test_runner")

    seasons_for_test = pd.read_csv(os.path.join(OUTPUT_DIR, "seasons_ground_truth.csv"))
    seasons_for_test["start_date"] = pd.to_datetime(seasons_for_test["start_date"])
    seasons_for_test["peak_date"] = pd.to_datetime(seasons_for_test["peak_date"])
    seasons_for_test["end_date"] = pd.to_datetime(seasons_for_test["end_date"])

    bm_lead_df = test_runner.test_bm_lead_time(bm_signals, seasons_for_test)
    bm_false_df = test_runner.test_bm_false_signal(bm_signals, seasons_for_test)
    roc_lead_df = test_runner.test_ethroc_lead_time(ethroc_signals, seasons_for_test)

    alt_returns = returns_df["altcoin_mkt_return"]
    roc_false_df = test_runner.test_ethroc_false_alarm(ethroc_signals, alt_returns)

    # Generate all 6 charts
    print("\nGenerating charts...")

    print("  Chart 1: Ground Truth Seasons")
    chart_ground_truth(seasons, returns_df)

    print("  Chart 2: BM Method Comparison")
    chart_bm_comparison(seasons, bm_signals)

    print("  Chart 3: ETH/BTC ROC Method Comparison")
    chart_ethroc_comparison(seasons, ethroc_signals)

    print("  Chart 4: Lead Time Boxplot")
    chart_lead_time_boxplot_from_data(bm_lead_df, roc_lead_df)

    print("  Chart 5: Noise Comparison")
    chart_noise_comparison(bm_false_df, roc_false_df)

    print("  Chart 6: Combined Score Heatmap")
    chart_combined_heatmap(combined)

    print(f"\nAll charts saved to: {CHARTS_DIR}")


if __name__ == "__main__":
    main()
