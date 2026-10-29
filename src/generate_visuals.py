"""Regenerate the public aggregate charts from committed CSV files."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
VISUALS = ROOT / "visuals"
COLORS = {"positive": "#2A9D8F", "neutral": "#8D99AE", "negative": "#E76F51"}


def sentiment_by_platform() -> None:
    frame = pd.read_csv(DATA / "aggregate-sentiment-by-platform.csv").melt(
        id_vars="sentiment_label", var_name="platform", value_name="share"
    )
    frame["share"] *= 100
    fig, ax = plt.subplots(figsize=(11, 6))
    sns.barplot(data=frame, x="sentiment_label", y="share", hue="platform", ax=ax)
    ax.set(title="Sentiment comparison by public source", xlabel="Sentiment", ylabel="Share of records (%)")
    ax.set_ylim(0, 70)
    for container in ax.containers:
        ax.bar_label(container, fmt="%.1f%%", padding=3)
    sns.despine()
    fig.tight_layout()
    fig.savefig(VISUALS / "sentiment-comparison.png", dpi=180)
    plt.close(fig)


def sentiment_by_theme() -> None:
    frame = pd.read_csv(DATA / "theme-sentiment-counts.csv").drop(columns="total").melt(
        id_vars="theme", var_name="sentiment", value_name="records"
    )
    fig, ax = plt.subplots(figsize=(13, 7))
    sns.barplot(
        data=frame,
        x="theme",
        y="records",
        hue="sentiment",
        hue_order=["positive", "neutral", "negative"],
        palette=COLORS,
        ax=ax,
    )
    ax.set(title="Employee sentiment by multi-label theme", xlabel="", ylabel="Number of tagged records")
    ax.tick_params(axis="x", rotation=8)
    for container in ax.containers:
        ax.bar_label(container, padding=3)
    sns.despine()
    fig.tight_layout()
    fig.savefig(VISUALS / "sentiment-by-theme.png", dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    VISUALS.mkdir(exist_ok=True)
    sentiment_by_platform()
    sentiment_by_theme()
    print(f"Charts written to {VISUALS}")

