# EDA Insights

From `notebooks/01_eda.ipynb`, executed end-to-end locally on **2026-09-01**
(~21 s wall-clock; kernel Python 3.11.15, sklearn 1.9.0 — full version
snapshot in the notebook's closing cell). Findings first, evidence after,
per `docs/0_coding_standards.md`. Every number below is read from that
executed run.

## 1. Schema Confirmed — and No Missingness Workstream

`train.csv`: 668,665 × 15. `test.csv`: 286,571 × 14. 13 features (7 numeric,
6 categorical), `id`, target `Will_Buy_EV`. **Zero missing values in either
split** (asserted over every column). The entire missingness apparatus that
S6E8 needed — indicator ablations, rate-drift checks — is simply absent
here.

## 2. Target Confirmed

Positive rate `116,779 / 668,665 = 0.174645` (No: 82.54%). The
`sample_submission.csv` constant is exactly `0.174645` in all 286,571 rows —
the expected submission is `P(Will_Buy_EV = "Yes")`, and the organizers'
reference baseline is the train prevalence.

## 3. Feature Signal Is Extremely Top-Heavy

Univariate diagnostics on the full train set (numeric: orientation-free
univariate AUC + Cohen's *d*; categorical: level-rate AUC — EDA diagnostic
only, leaky as a fold-external model feature):

| Feature | Univariate AUC | Note |
| --- | ---: | --- |
| `Environmental_Concern_Level` | **0.8435** | Cohen's *d* 1.56 — dominant |
| `Subsidy_Available` | **0.7179** | binary gate, see §5 |
| `Annual_Income_USD` | 0.6704 | *d* 0.62 — clear second tier |
| `Home_Charging_Possible` | 0.5508 | 12.71% vs. 19.58% |
| `Range_Anxiety_Level` | 0.5451 | monotone, see §4 |
| `Daily_Commute_km` | 0.5338 | near-noise |
| `City_Type` | 0.5234 | Rural 19.3% / Urban 16.1% |
| `Charging_Stations_Near_Home` | 0.5159 | near-noise |
| `Charging_Stations_Near_Work` | 0.5106 | near-noise |
| `Current_Car_Type` | 0.5104 | Truck 15.6% / SUV 18.1% |
| `Age` | 0.5055 | noise-level |
| `Gender` | 0.5046 | noise-level |
| `Number_of_Cars_Owned` | 0.5039 | noise-level |

Mutual information (150k stratified subsample, seed 42) agrees with this
ranking and finds **no hidden nonlinear heavyweight** among the weak
features (MI ≤ 0.004 outside the top five). The S6E8 situation — MI rescuing
Pearson-invisible features — does not recur.

## 4. Both Ordinal Candidates Are Strictly Monotone

- `Environmental_Concern_Level` (discrete 1–5, stored float): positive rate
  0.57% → 2.14% → 11.09% → 24.88% → **51.83%**. Already numeric; keep
  numeric.
- `Range_Anxiety_Level`: Low 18.90% → Medium 4.17% → High **0.14%**
  (High n = 2,194, SE ≈ 0.08 points — rare but precisely estimated).
  Ordinal encoding (Low=0 < Medium=1 < High=2) is the justified default for
  GBDTs; treat-as-categorical is the cheap A/B, the reverse of S6E8's
  non-monotonic `stress_level`.

## 5. The Subsidy Gate — the Dataset's One Big Interaction

`Subsidy_Available` splits the population into two regimes:

| | Subsidy = No | Subsidy = Yes |
| --- | ---: | ---: |
| Home charging = No | 0.40% | 20.6% |
| Home charging = Yes | 0.66% | **30.4%** |

Without a subsidy, purchase probability is under 0.7% *regardless of home
charging*; with one, home charging adds ~10 points. Tree ensembles capture
this natively; only a linear baseline needs the explicit product. The
charging-station counts stay near-flat in both regimes, consistent with
their ≈0.51 univariate AUC.

## 6. Duplicates: Exactly Zero, All Three Ways

Train-internal 0, test-internal 0, cross-set (test feature tuple appearing
in train) 0. No duplication leakage channel, no membership tricks.

## 7. Train/Test Are Statistically Indistinguishable

- **Numeric (KS):** statistic ≤ 0.003 on every feature; most p-values
  non-significant even at n ≈ 10⁶. Only range difference:
  `Daily_Commute_km` test max 103.9 vs. train 98.7 — a 5 km extension on a
  handful of rows; trees extrapolate flat, no action.
- **Categorical:** max proportion delta ≤ 0.17 points.
  `Range_Anxiety_Level`'s chi-square p = 0.002 reflects the enormous n, not
  a material shift.
- **Adversarial validation:** 3-fold OOF `HistGradientBoostingClassifier`
  (native categoricals) AUC = **0.4992** — indistinguishable; the
  permutation drill-down was skipped by the predeclared ≥ 0.55 rule.

Practical consequence: **local CV should track the leaderboard closely.**
Any future CV-vs-LB gap points at modeling (overfitting, leakage), not
drift.

## 8. Runtime Reality Check (Scale Override Context)

`docs/0_coding_standards.md` flags this competition's data as large enough
to require measurement before sweeps. First evidence: the full EDA —
including a 3-fold HGB adversarial fit over all 955,236 combined rows — ran
in **~21 s** locally. The scale override stays in force (measure the first
full-data *model* fit before any sweep), but the data is lighter than the
7.7 MB sample-submission size implied.

## 9. Next Moves (Baseline Phase Priority Order)

This section is the **only** home for the EDA's forward plan — the
notebook itself carries findings only (`docs/0_coding_standards.md`).

1. Fixed folds, defined once: `StratifiedKFold(n_splits=5, shuffle=True,
   random_state=42)`; recorded in the experiment ledger at first use.
2. v1 sanity: constant, logistic (one-hot + scaled), default HGB — with
   wall-clock and memory measured on the first full fit.
3. v2 strong: LightGBM + CatBoost, native categoricals;
   `Range_Anxiety_Level` ordinal by default with a categorical A/B.
4. Explicit interaction crosses (`Subsidy × Environmental_Concern`,
   `Subsidy × Income`) only as an OOF-gated experiment if baselines plateau.
5. Expect a tight plateau (three features carry nearly all marginal
   signal) — the paired-OOF promotion gate is what separates real gains
   from noise; derive its width from this dataset's own fold std.
6. Explicitly **not** needed: missingness handling, drift correction,
   duplicate handling (§§1, 6–7).


## 10. Post-hoc: the numeric columns are value identities (2026-09-03)

Found after E05, from local diagnostics rather than the EDA notebook;
recorded here because it changes what "7 numeric features" means.

- `Annual_Income_USD`: 13,214 distinct values; 492 values occur ≥200
  times each and cover 32% of rows; `30000` alone is 9.2% of rows.
  `Daily_Commute_km`: 805 distinct values, `5.0` on 21.6% of rows.
  `Age` (45), `Charging_Stations_*` (15/20), `Number_of_Cars_Owned` (4),
  `Environmental_Concern_Level` (5) are small integer sets.
- 97.9% of train incomes are values present in the source dataset's
  8,915 incomes; the frequent ones are incomes the source lists 2–3
  times. The generator sampled the value, not a distribution.
- The exact value carries target signal beyond its magnitude: OOF target
  encoding of the exact income scores AUC 0.7072 vs 0.6812 for 100
  quantile bins. Rows whose income maps to a unique source row buy at
  26.1% when that row's label is Yes vs 17.6% when No.
- Tree quantization (254 borders) cannot isolate one value in 13k, so no
  model so far has used this. Tested as E06 (`docs/4_experiment_ledger.md`).
