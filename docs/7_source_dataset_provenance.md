# Source Dataset Provenance

**Identified 2026-09-02** — the item listed as open in
`docs/1_instructions.md` since the project began.

## The dataset

| Item | Value |
|---|---|
| Ref | [`itzzomkar/ev-adoption-behavior-and-range-anxiety`](https://www.kaggle.com/datasets/itzzomkar/ev-adoption-behavior-and-range-anxiety) |
| Title | EV Adoption Behavior and Range Anxiety |
| Owner | Omkar Kadam (`itzzomkar`) |
| **License** | **CC0-1.0 (CC0: Public Domain)** — no restriction on use |
| Rows | 10,000 × 15 (14 features + `Buyer_ID`) |
| Published | 2026-07-06, i.e. **before** the competition data (2026-08-12) |

Found via `kaggle datasets list -s "electric vehicle purchase prediction"`
after the competition's Data tab proved unfetchable (client-rendered) and
a column-name web search on 2026-09-01 returned nothing. The CLI's dataset
search was the tool that worked — worth remembering.

## Evidence it is the source

Verified against `data/train.csv` locally, not asserted:

1. **All 14 competition columns match by exact name**, including the
   distinctive `Range_Anxiety_Level`, `Charging_Stations_Near_Home/Work`,
   and the target `Will_Buy_EV`. The only extra column is the source's own
   `Buyer_ID`. Zero competition columns are absent from the source.
2. **Target prevalence:** source 17.50% positive vs. competition 17.46% —
   within sampling noise.
3. **Five of seven numeric ranges match exactly:** `Age` (25–69),
   `Number_of_Cars_Owned` (1–4), `Charging_Stations_Near_Home` (0–14),
   `Charging_Stations_Near_Work` (0–19), `Environmental_Concern_Level`
   (1–5).
4. **All six categorical vocabularies are identical** — same levels, no
   extras on either side.
5. The source's own description names the same two target variables and
   the same framing ("Predicting Electric Vehicle Purchase Intent based on
   Demographics and Infrastructure").

**Where they differ, consistently with generation:**

- `Annual_Income_USD` max 223,345 (source) vs. 188,549 (competition);
  `Daily_Commute_km` max 135.5 vs. 98.7 — the source has the wider tails,
  as expected when a generator is fit to it and resampled.
- The source carries ~1.8% missing values in `Annual_Income_USD`,
  `Daily_Commute_km` and `Environmental_Concern_Level` — deliberately
  introduced by its author "to allow beginners to practice Data Cleaning".
  The competition data has **none**, so the generator resolved them.
- **Zero source rows appear verbatim in competition train** — this is
  extra data, not a leak, and no membership signal exists.

## What it is (and what that implies)

The source is itself **synthetic**: its author states it was "generated via
a custom Python script" with distributions "modeled to reflect real-world
consumer challenges". So this is not real survey data feeding a synthetic
competition — it is a synthetic ancestor of a synthetic dataset.

Consequence for expectations: the usual argument for adding original data
("real rows carry signal the generator smoothed away") is **weaker here**,
because there were never real rows. Combined with size — 10,000 rows is
**1.5%** of the 668,665 training rows — the honest prior is that this adds
little. It is still worth one disciplined test, because it is the last
untested lever and it is cheap; it is not worth optimism.

## Usage rules

- CC0 permits use without attribution, but the dataset is cited here and
  in any submission description that depends on it.
- If used as extra training data, source rows go into **training folds
  only** — never into a validation fold, so OOF stays measured purely on
  competition data (master standard §5).
- Rows with missing values are dropped before use (9,466 remain per the
  kernel v8 count; an earlier local count said 9,478), so the
  training distribution keeps the competition's no-missing regime rather
  than teaching the model a NaN branch that can never fire at test time.

## Outcome — two different uses, only one of them null

**As extra training rows (E05, 2026-09-02): null.** Appended to the
training portion of each fold, it moved OOF +0.00001, 95% CI (−0.000049,
+0.000073), P(Δ>0) = 0.627. That use is closed.

**As a feature (E06 onward, 2026-09-03): in use by the champion.** E06
reintroduced the dataset in a different role — a per-income lookup of the
*source rows' own* label rate and count (`Src_Income_Rate`,
`Src_Income_N`), which touches no competition target and so needs no fold
handling. The champion `e08_avg3seeds` is fit on features v3 **plus this
lookup**, as were E07 and E09, and the kernel attaches the dataset via
`notebooks/kernels/baseline_modeling/kernel-metadata.json`.

**The citation obligation in "Usage rules" above is therefore live**, not
hypothetical: submissions 4, 5, 6 and 7 all depend on this dataset.

**Caveat worth recording:** E06 Finding 2 measured the lookup's own
contribution at **+0.000018** — indistinguishable from zero, and below
even the current 0.00005 noise floor. The champion could drop the
dependency for about −0.00002. It carries it only because the predeclared
rule was "the higher-OOF arm wins" and the lookup arm won by that margin.

*(An earlier version of this section read "The dataset is not used by the
champion and will not be used in any submission." That was written after
E05 and was already false once E06 landed; corrected 2026-09-04.)*
