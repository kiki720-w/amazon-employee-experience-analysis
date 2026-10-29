# Methodology

## 1. Scope and evidence boundary

The original project used 144 public records: 139 Glassdoor entries and five YouTube records. The repository contains only aggregate outputs. Raw review text, transcripts, names, locations, links and platform identifiers are excluded.

The sample is exploratory. It is suitable for generating operational hypotheses, not for estimating workforce-wide prevalence or making decisions about individuals.

## 2. Text preparation

The pipeline:

1. combines the authorized text fields;
2. decodes HTML entities and normalizes case;
3. removes URLs, email addresses and non-word characters;
4. removes common English stop words for keyword analysis;
5. retains a sanitized text field only during local processing.

## 3. Keyword analysis

Unigrams, bigrams and trigrams are extracted using `CountVectorizer`. Terms are ranked by document-level occurrence. Keyword frequencies are descriptive and are interpreted alongside theme and sentiment results.

## 4. Sentiment

TextBlob polarity is used as a transparent baseline:

- positive: polarity greater than `0.05`;
- negative: polarity below `-0.05`;
- neutral: all remaining values.

This baseline is intentionally simple and auditable. Human review is recommended for high-impact use.

## 5. Theme taxonomy

Each record may receive multiple labels when its cleaned text matches published keyword rules:

- **Workload, Scheduling & Recovery:** shift, schedule, overtime, break, physical demands, fatigue, stress, productivity targets and work-life balance.
- **Frontline Management & Growth:** manager support, communication, training, recognition, promotion and culture.
- **Compensation & Benefits:** pay, wages, benefits, bonuses, holiday pay and tuition support.

Records with no match are marked `Other / Unclassified`. In the source analysis, 112 of 144 records received at least one theme, producing 77.8% tagging coverage.

## 6. Decision framework

Themes were compared using volume, negative count, operational actionability and reversibility of a possible intervention. Workload, scheduling and recovery was selected for a pilot because it combined the highest frequency with the largest negative count.

## 7. Validation requirements

Before operational use, the organization should:

- validate the taxonomy with employees and site leaders;
- audit a sample of labels manually;
- compare findings with internal workforce data;
- review privacy, labor-relations and legal implications;
- test the intervention in a controlled, reversible pilot.

