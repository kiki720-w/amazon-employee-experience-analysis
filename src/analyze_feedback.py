"""Aggregate-only employee-feedback analysis.

The script expects an authorized CSV with a `text` column and an optional
`platform` column. It writes aggregates but never copies raw text to output.
"""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from textblob import TextBlob


THEMES = {
    "Workload, Scheduling & Recovery": [
        "hours", "long hours", "shift", "schedule", "night", "sleep",
        "overtime", "break", "physical", "physically", "demanding",
        "standing", "fast paced", "overwork", "tired", "exhausted",
        "stress", "rate", "target", "productivity", "work life", "workload",
    ],
    "Frontline Management & Growth": [
        "management", "manager", "leadership", "leader", "supervisor",
        "communication", "training", "onboarding", "support", "micromanage",
        "favoritism", "recognition", "promote", "promotion", "career",
        "growth", "opportunity", "culture", "write up",
    ],
    "Compensation & Benefits": [
        "pay", "salary", "wage", "benefit", "bonus", "holiday pay",
        "tuition", "reimbursement", "compensation",
    ],
}


def clean_text(value: object) -> str:
    text = html.unescape(str(value or "")).lower()
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"\b[\w.+-]+@[\w.-]+\.[a-z]{2,}\b", " ", text)
    text = re.sub(r"[^a-z0-9\s'-]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def sentiment_label(text: str) -> tuple[float, str]:
    polarity = float(TextBlob(text).sentiment.polarity)
    label = "positive" if polarity > 0.05 else "negative" if polarity < -0.05 else "neutral"
    return polarity, label


def theme_labels(text: str) -> list[str]:
    labels = [name for name, keywords in THEMES.items() if any(keyword in text for keyword in keywords)]
    return labels or ["Other / Unclassified"]


def top_ngrams(texts: pd.Series, ngram_range: tuple[int, int], limit: int = 25) -> pd.DataFrame:
    vectorizer = CountVectorizer(stop_words="english", ngram_range=ngram_range, min_df=1)
    matrix = vectorizer.fit_transform(texts)
    counts = matrix.sum(axis=0).A1
    return (
        pd.DataFrame({"term": vectorizer.get_feature_names_out(), "count": counts})
        .sort_values(["count", "term"], ascending=[False, True])
        .head(limit)
    )


def run(input_path: Path, output_dir: Path) -> None:
    frame = pd.read_csv(input_path)
    if "text" not in frame.columns:
        raise ValueError("Input CSV must contain a 'text' column.")

    frame["platform"] = frame.get("platform", pd.Series("Unknown", index=frame.index)).fillna("Unknown")
    frame["clean_text"] = frame["text"].map(clean_text)
    scored = frame["clean_text"].map(sentiment_label)
    frame[["sentiment_polarity", "sentiment_label"]] = pd.DataFrame(scored.tolist(), index=frame.index)
    frame["theme"] = frame["clean_text"].map(theme_labels)

    output_dir.mkdir(parents=True, exist_ok=True)

    platform = pd.crosstab(frame["sentiment_label"], frame["platform"], normalize="columns")
    platform.to_csv(output_dir / "aggregate-sentiment-by-platform.csv")

    exploded = frame[["theme", "sentiment_label"]].explode("theme")
    theme_counts = pd.crosstab(exploded["theme"], exploded["sentiment_label"])
    theme_counts["total"] = theme_counts.sum(axis=1)
    theme_counts.to_csv(output_dir / "theme-sentiment-counts.csv")

    for n in (1, 2, 3):
        top_ngrams(frame["clean_text"], (n, n)).to_csv(output_dir / f"top-{n}grams.csv", index=False)

    print(f"Processed {len(frame)} authorized records; wrote aggregate-only outputs to {output_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("output"))
    args = parser.parse_args()
    run(args.input_csv, args.output_dir)


if __name__ == "__main__":
    main()

