# Wine Quality Prediction Using Ensemble Learning

### A reproduction of Ma et al. (2024), *Journal of Business Research*

**Author:** SURIANANDHAN S · **Register number:** 127018060
**Course:** CSE425 — Machine Learning Essentials
**Guide:** Dr. Vidivelli S, AP-II · Department of CSE, School of Computing
**Base paper:** Ma, R., Mao, D., Cao, D., Luo, S., Gupta, S., & Wang, Y. (2024). From
vineyard to table: Uncovering wine quality for sales management through machine
learning. *Journal of Business Research*, 176, 114576.
https://doi.org/10.1016/j.jbusres.2024.114576
**Dataset:** UCI Wine Quality (Red), https://archive.ics.uci.edu/dataset/186/wine+quality

---

## 1. Introduction

Wine retailers have a practical problem: physicochemical lab tests are cheap and
objective, but the quality score that actually drives pricing and shelf placement comes
from a subjective sensory panel. Ma et al. (2024) propose learning a mapping from the
11 lab-measured attributes of a red wine to its quality score, using an ensemble of
four learners weighted by both accuracy and diversity. They report 89.73% overall
accuracy — a large figure for this dataset.

This project reproduces that framework under a classical-ML-only constraint, using the
same dataset and the same weighting equations. The reproduction reaches **69.01%**. The
bulk of this report is devoted to establishing, from the paper's own published tables,
*why* the two numbers differ — which turns out to be the most informative part of the
exercise.

## 2. Base paper summary

Ma et al. use 1,599 red *Vinho Verde* samples (originally from Cortez et al., 2009),
each with 11 physicochemical attributes and a quality score assigned by a
three-sommelier panel. After min-max normalising the attributes, four base learners —
SVM, RNN, ELM, and Random Forest — are each trained under 10-fold cross-validation.
Their predictions are then combined by a weighted sum (Eq. 1), where each learner's
weight is the average of:

- an **accuracy-based weight** (Eq. 5), the normalised inverse of its CV error, and
- a **diversity-based weight** (Eq. 9), the normalised sum of Euclidean distances
  between its per-sample error vector and every other learner's (Eqs. 7-8).

The paper reports individual accuracies of 67.30% (SVM), 61.43% (RNN), 55.77% (ELM),
and 80.71% (RF), and an ensemble accuracy of 89.73% — a 9.02-point improvement over the
best single learner. Extreme quality classes (3, 4, 8) remain the weakest, which the
paper attributes to their small sample sizes (10, 53, and 18 samples respectively).

## 3. Methodology

### 3.1 Substitutions required by the syllabus

Two of the four base learners fall outside a classical-ML-only syllabus:

| Paper's learner | Why out of scope | Substitute | Rationale |
|---|---|---|---|
| RNN | Deep-learning sequence model; needs backprop-through-time | `GradientBoostingClassifier` | Each new tree fits the residual errors of those before it — a classical-ML analogue of iterative refinement. The brief permits AdaBoost or Gradient Boosting; we use GB because AdaBoost's default depth-1 stumps scored around 49% in an early exploratory run — an informal observation, not recorded in `results/` |
| ELM | Random fixed hidden weights + closed-form output layer; explicitly *not* backprop | `MLPClassifier` | Closest analogue that is still a neural network, but trained end-to-end by standard backpropagation |
| SVM | Already classical ML | `SVC` (unchanged) | — |
| Random Forest | Already classical ML | `RandomForestClassifier` (unchanged) | — |

### 3.2 Pipeline

`src/preprocessing.py` → `src/base_learners.py` → `src/ensemble.py` → `src/evaluate.py`.

1. Load 1,599 rows; keep all of them (no class is dropped or merged).
2. Fit each learner under stratified 10-fold CV, with **min-max scaling inside a
   `Pipeline`** so the scaler sees only the training fold. This preserves the paper's
   normalisation step (its Fig. 2) without leaking test-fold statistics into the scaling
   constants — an earlier version of this project scaled the full matrix once up front,
   which inflates results.
3. Compute the paper's weights from each repeat's out-of-fold errors (Eqs. 4-9).
4. Combine predictions (see 3.3).
5. Repeat the entire 10-fold CV **10 times** with different splits — 100 fold-runs,
   matching the paper's stated protocol — and pool all out-of-fold predictions before
   computing final metrics.

Because classes 3 and 8 hold only 10 and 18 samples, SVM and RF use balanced class
weights so the minority classes contribute to the loss rather than being ignored. The
paper does not state any imbalance handling; this is our own explicit choice.

### 3.3 Two readings of Eq. (1)

Eq. (1) is a weighted **sum**, `ŷ = Σ wᵢ ŷᵢ`. What `ŷᵢ` denotes changes the result:

- **Soft vote** — `ŷᵢ` is the per-class probability vector, so `P = Σ wᵢ·Pᵢ` and the
  prediction is `argmax(P)`. This is the literal reading of the equation.
- **Hard vote** — `ŷᵢ` is a one-hot class label, so the sum degenerates into weighted
  majority voting.

We implement and report both, since the choice is a genuine ambiguity in the paper.

### 3.4 Evaluation and a terminology correction

Ma et al. label their per-class metric "precision", but their own worked example
(Eq. 14: `137/(137+1+2+58+6)` for class 5) divides the diagonal by the **actual class
total** — that is TP/(TP+FN), i.e. recall/sensitivity, not TP/(TP+FP). Our
reconciliation confirms this empirically: 4 of their 6 published per-class values
reproduce **column-wise** from their own confusion matrix (3 of them exactly; class 6
matches only to within 0.6 points), against just 1 of 6 that reproduces
row-wise. We therefore report their metric under their definition (so the comparison is
like-for-like) while also reporting conventional precision, recall, and specificity
separately in `results/tables/metrics_*.csv`.

## 4. Results

*All figures below come from `results/tables/*.csv`, generated by `python run_all.py`
(10-fold CV × 10 repeats, seeds 0-9).*

### 4.1 Model ranking

| Rank | Model | Overall accuracy |
|---|---|---|
| 1 | Random Forest | **71.03%** |
| 2 | Ensemble (hard vote) | 69.93% |
| 3 | Ensemble (soft vote) | 69.01% |
| 4 | GradientBoosting (substitutes RNN) | 67.67% |
| 5 | SVM | 61.95% |
| 6 | MLP (substitutes ELM) | 61.35% |

**The paper's central claim does not reproduce.** Ma et al. report their ensemble
beating the best single learner by 9.02 points; ours falls 2.02 points *below* Random
Forest. Section 4.3 explains why, and argues this is a property of the method rather
than a defect in our implementation.

A secondary result: soft voting (69.01%) scored marginally *below* hard voting
(69.93%) overall, contrary to our expectation. Soft voting did recover some class-4
samples (0.57% recall) where hard voting recovers none (0.00%), but that difference is
3 correct predictions out of 530 pooled instances and classes 3 and 8 are identical
under both schemes — too small to claim a general minority-class advantage. We report
the soft vote as the headline ensemble because it is the literal reading of Eq. (1),
not because it scored higher.

### 4.2 Per-class comparison against published benchmarks

Per-class values use the paper's own metric definition (= recall).

| Class | n | Cortez et al. (2009) | Ma et al. (2024) | Our reproduction |
|---|---|---|---|---|
| 3 | 10 | 0.00% | 33.33% | 0.00% |
| 4 | 53 | 20.00% | 63.16% | 0.57% |
| 5 | 681 | 67.50% | 84.80% | **81.66%** |
| 6 | 638 | 57.70% | 88.06% | **69.87%** |
| 7 | 199 | 58.60% | 77.08% | 49.90% |
| 8 | 18 | 0.00% | 50.00% | 11.11% |
| **Overall** | 1599 | — | **89.73%** | **69.01%** |

The shape of the paper's finding does reproduce: the well-populated mid-tier classes
(5, 6) are predicted far above the Cortez et al. baseline, and the extreme classes stay
hardest. Class 3 remains at 0.00% — with 10 samples spread across 10 folds, roughly one
sample per test fold, no learner in this family recovers it. We report that rather than
tuning until it moves.

### 4.3 Why 89.73% does not reproduce

Two independent checks, both computed in code from the paper's own printed numbers
(`src/evaluate.py`), so a reader can verify them.

**(a) Their Table 9 confusion matrix implies a different protocol and a different
accuracy.** Summing every cell of the ensemble confusion matrix gives **491 samples** —
30.7% of the dataset, i.e. a single hold-out split, not the 100-run cross-validation the
text describes. Our protocol scores all 1,599 samples ten times over, which is strictly
harder. Furthermore, the diagonal of that same matrix gives **403/491 = 82.08%**, which
is **7.65 points below** the 89.73% reported in the text.

**(b) Their Table 8 weights, applied to their Tables 4-7 accuracies, imply ~67.5%.**
The paper's final weights are 0.2516 (SVM), 0.2286 (RNN), 0.2168 (ELM), 0.3030 (RF) —
never more than 0.053 away from a uniform 0.25. Applying those weights to their reported
base accuracies gives a weighted average of **67.52%**.

| Quantity | Value |
|---|---|
| Weighted average of the paper's own base accuracies | 67.52% |
| Paper's reported ensemble accuracy | 89.73% |
| Gap | **+22.21 points** |
| **Our reproduction's ensemble** | **69.01%** |
| Our gap vs. that weighted average | **+1.49 points** |

A voting ensemble is not merely the weighted average of its members' accuracies —
decorrelated errors legitimately let a good ensemble exceed that baseline — so this is
an indicative reference point, not a proof. But our result sits 1.49 points above it,
while the paper's sits 22.21 points above it.

This also explains our own ranking in 4.1. Our measured weights span only
0.2356-0.2698, a maximum deviation of 0.0198 from uniform. Eqs. (5) and (9) normalise
inverse errors and pairwise error distances, and neither discriminates sharply when the
base learners have broadly similar error rates. With weights this flat, the ensemble
approximates an unweighted average of its four members — and an average of one strong
learner and three weaker ones necessarily lands *between* them, not above the strongest.
Our ensemble beating three of its four members while trailing Random Forest is exactly
the behaviour the equations predict.

**Caveat.** The Table 9 cells were transcribed by eye from the printed PDF and may
contain reading errors — two of the six per-class values (classes 7 and 8) do not
reproduce column-wise, most plausibly for that reason. We therefore report this as *we
could not reconcile these figures*, not as a claim that the paper is incorrect.

**Context.** Published accuracies for the 6-class UCI red wine task typically fall in
the 62-72% range. Our 69.01% sits inside that band; 89.73% sits well above it.

## 5. Conclusion

The reproduction succeeds structurally and fails numerically, and the failure is the
informative part.

Structurally, everything the paper specifies was implemented as written: the four base
learners (two substituted for syllabus reasons), the accuracy and diversity weighting of
Eqs. (4)-(9), min-max preprocessing, and the 10×10 cross-validation protocol. The
qualitative pattern reproduces — mid-tier classes are predicted well, extreme classes
poorly, and the class-imbalance limitation the paper acknowledges is real and severe.

Numerically, we reach 69.01% against a reported 89.73%, and our ensemble does not
overtake Random Forest. We do not attribute this to the substituted learners: the
paper's own Table 8 weights are near-uniform, its own base-learner accuracies imply an
ensemble around 67.5%, and its own Table 9 confusion matrix implies both a ~490-sample
hold-out and an 82% accuracy. Our 69.01% is within 1.5 points of what the paper's
published numbers imply, and inside the range this dataset normally produces.

The methodological lesson is that an accuracy-and-diversity weighting scheme that
normalises across similar learners produces weights too flat to let a strong learner
dominate — so on an imbalanced multiclass problem, such an ensemble tends to average
toward its members rather than exceed the best of them.

---

<!-- REVIEW2-SECTION:BEGIN -->
<!-- Generated by presentation/build_review2_docs.py from results/review2/tables -- do not edit by hand. -->

## 6. Review 2 — class balancing, improving the result, feature importance

At the first review the guide asked for three changes: class balancing (only partially
present), an improved result, and feature importance. This section reports all three. The
code is in `src/review2.py` and `src/feature_importance.py`, run by `python run_all.py --review2`.

### 6.1 Protocol, primary metric and disclosures

Every Review-2 experiment uses the reproduction's protocol unchanged: stratified 10-fold
cross-validation × 10 repeats with fold seeds 0–9, and every scaler, resampler and feature
selector fitted inside the training fold. Results go to `results/review2/`, so the Review-1
numbers remain the baseline.

The primary metric is **macro-F1**, fixed in `config.py` before any Review-2 experiment ran.
Classes 5 and 6 hold 82.5% of the data, so accuracy can stay high while the rare classes are
missed entirely — the Review-1 ensemble scores 69.01% accuracy with 0.0% recall on
class 3 and 0.6% on class 4. Class balancing deliberately trades common-class accuracy
for rare-class recall, so accuracy alone would judge it on the one thing it gives up.

Two disclosures. (i) The best model is selected on the same cross-validation that scores
it, which biases its score slightly upwards. (ii) Two candidates (the learned-temperature
ensemble and the balanced-combiner stack) were added after a one-repeat smoke test; both
choose their settings inside each training fold, never from the test folds.

### 6.2 Class balancing

Four schemes were compared on the reproduction's four learners and weighted soft vote, so
that balancing is the only variable: no balancing; Review 1's partial scheme (balanced class
weights on SVM and Random Forest); balanced weights on all four (MLP and GradientBoosting
have no `class_weight` parameter, so they receive the equivalent per-sample weights); and
SMOTE oversampling (Chawla et al., 2002). SMOTE runs inside the pipeline after the scaler,
so synthetic samples are built from training-fold wines only.

| Scheme | Accuracy | Bal. acc. | Macro-F1 | Rec. 3 | Rec. 4 | Rec. 5 | Rec. 6 | Rec. 7 | Rec. 8 |
|---|---|---|---|---|---|---|---|---|---|
| No balancing | 68.82 | 35.28 | 36.64 | 0.0 | 0.2 | 81.5 | 69.9 | 49.0 | 11.1 |
| Review 1 (SVM + RF only) | 69.01 | 35.52 | 36.92 | 0.0 | 0.6 | 81.7 | 69.9 | 49.9 | 11.1 |
| Class weights, all four | 68.43 | 37.94 | 38.77 | 0.0 | 7.7 | 80.3 | 65.5 | 61.9 | 12.2 |
| SMOTE oversampling | 63.86 | 41.44 | 39.34 | 10.0 | 26.4 | 73.0 | 59.2 | 64.5 | 15.6 |

SMOTE oversampling gives the best macro-F1. Balancing moves recall from the two majority
classes to the rare ones: with SMOTE, class-4 recall rises from 0.6% to 26.4% and
class 7 from 49.9% to 64.5%, while accuracy falls 5.15 points. Figure:
`results/review2/figures/A_class_balancing.png`.

### 6.3 Improving the result

**Testing the Review-1 diagnosis (diagnostic only).** Review 1 attributed the ensemble's
failure to beat Random Forest to near-uniform weights. Raising the paper's weights to a
power T before normalising tests that directly (T = 1 is the paper). Because these weights
are computed from the same out-of-fold predictions they are scored on, the sweep is never
used to select a model.

| T | Accuracy (accuracy term sharpened) | Largest weight | Accuracy (both terms sharpened) |
|---|---|---|---|
| 1 | 69.01 | 0.270 | 69.01 |
| 2 | 69.22 | 0.293 | 69.20 |
| 5 | 69.90 | 0.364 | 69.82 |
| 10 | 70.78 | 0.466 | 70.59 |
| 25 | 71.22 | 0.590 | 71.08 |
| 100 | 71.23 | 0.623 | 70.41 |

Random Forest alone scores 71.03%. Sharpening the accuracy term overtakes Random Forest from T = 25. Sharpening
the diversity term as well eventually backfires: it concentrates weight on the learner whose
errors differ most from the others, which is usually the weakest.

**The fix, done properly (learned temperature).** The same scheme, but each outer training
fold runs an inner 5-fold cross-validation to choose T and whether to sharpen one term or
both, on the primary metric. The outer test fold never influences the choice. With the
reproduction's own four learners this raises accuracy from 69.01% to 70.89% and
macro-F1 from 36.92 to 38.08; the inner CV chose a sharp temperature (T ≥ 10)
in 99% of the 100 folds. With SMOTE members it reaches a macro-F1 of 40.87.

**Stacking and stronger members.** A logistic-regression combiner (Wolpert, 1992) trained on
the members' out-of-fold probabilities reaches 70.92% accuracy but only 34.96
macro-F1 — it relearns the majority-class bias. A class-balanced combiner swings the other way
(59.20% accuracy). ExtraTrees and HistGradientBoosting were also tried as members.

The ensembles, ranked on the primary metric:

| Rank | Ensemble | Accuracy | Bal. acc. | Macro-F1 |
|---|---|---|---|---|
| 2 | Learned-T ensemble · SMOTE | 66.63 | 42.49 | 40.87 |
| 3 | Paper ensemble · SMOTE | 63.86 | 41.44 | 39.34 |
| 4 | Paper ensemble · class weights | 68.43 | 37.94 | 38.77 |
| 9 | Learned-T ensemble · Review-1 setup | 70.89 | 36.58 | 38.08 |
| 10 | Paper weights: SVM + RF + ExtraTrees + HistGB | 70.79 | 36.96 | 38.04 |
| 12 | Stacked: paper's 4 learners, balanced combiner | 59.20 | 50.03 | 37.82 |
| 15 | Paper ensemble · Review-1 setup | 69.01 | 35.52 | 36.92 |
| 18 | Paper ensemble · no balancing | 68.82 | 35.28 | 36.64 |
| 19 | Stacked: SVM + RF + ExtraTrees + HistGB | 70.93 | 34.92 | 35.02 |
| 20 | Stacked: paper's 4 learners (class-weighted) | 70.92 | 35.04 | 34.96 |

No candidate is best on both metrics; `results/review2/figures/B_tradeoff.png` plots every
candidate's accuracy against its macro-F1 with the Pareto frontier marked.

**Consistency across repeats.** Every candidate was scored on identical folds in each of the
ten repeats, so their per-repeat scores can be paired:

| Model | Compared with | Metric | Mean diff. | Repeats won | Wilcoxon p |
|---|---|---|---|---|---|
| RF · SMOTE | Paper ensemble · Review-1 setup | macro-F1 | +3.97 | 10 / 10 | 0.002 |
| RF · SMOTE | Paper ensemble · Review-1 setup | accuracy | -1.08 | 1 / 10 | 0.004 |
| RF · SMOTE | RF · Review-1 setup | macro-F1 | +2.80 | 10 / 10 | 0.002 |
| RF · SMOTE | RF · Review-1 setup | accuracy | -3.10 | 0 / 10 | 0.002 |
| RF · SMOTE | Learned-T ensemble · SMOTE | macro-F1 | +0.01 | 4 / 10 | 0.846 |
| RF · SMOTE | Learned-T ensemble · SMOTE | accuracy | +1.31 | 9 / 10 | 0.006 |
| Learned-T ensemble · Review-1 setup | Paper ensemble · Review-1 setup | macro-F1 | +1.16 | 10 / 10 | 0.002 |
| Learned-T ensemble · Review-1 setup | Paper ensemble · Review-1 setup | accuracy | +1.88 | 10 / 10 | 0.002 |
| Learned-T ensemble · Review-1 setup | RF · Review-1 setup | macro-F1 | -0.01 | 6 / 10 | 0.922 |
| Learned-T ensemble · Review-1 setup | RF · Review-1 setup | accuracy | -0.14 | 4 / 10 | 0.438 |
| RF · Review-1 setup | Paper ensemble · Review-1 setup | macro-F1 | +1.17 | 10 / 10 | 0.002 |
| RF · Review-1 setup | Paper ensemble · Review-1 setup | accuracy | +2.02 | 10 / 10 | 0.002 |

The repeats reuse the same 1,599 wines with different splits, so they are not independent
samples and these p-values are optimistic; the win counts are the plainer evidence. A
corrected resampled t-test (Nadeau & Bengio, 2003) would give proper intervals.

### 6.4 Feature importance

Three measures were computed and checked against each other: permutation importance on the
held-out folds (the primary measure — macro-F1 lost when a feature is shuffled in the test
fold), Random Forest's impurity importance (MDI, which is biased towards continuous,
many-valued features; Strobl et al., 2007), and the Spearman correlation of each feature with
quality for the direction of effect.

| Rank | Feature | Perm., best model | Perm., RF | MDI, RF | Spearman ρ | Paper key |
|---|---|---|---|---|---|---|
| 1 | alcohol | 7.45 | 8.48 | 0.135 | +0.48 | yes |
| 2 | sulphates | 7.28 | 6.49 | 0.119 | +0.38 | yes |
| 3 | volatile acidity | 4.44 | 4.86 | 0.129 | -0.38 | yes |
| 4 | chlorides | 2.33 | 1.05 | 0.093 | -0.19 |  |
| 5 | total sulfur dioxide | 1.66 | 2.27 | 0.089 | -0.20 |  |
| 6 | citric acid | 0.56 | 1.39 | 0.079 | +0.21 | yes |
| 7 | fixed acidity | -0.13 | 0.34 | 0.068 | +0.11 |  |
| 8 | residual sugar | -0.15 | 0.34 | 0.065 | +0.03 |  |
| 9 | density | -0.50 | 0.67 | 0.085 | -0.18 |  |
| 10 | pH | -0.59 | 0.92 | 0.076 | -0.04 |  |
| 11 | free sulfur dioxide | -1.16 | 1.06 | 0.062 | -0.06 |  |

The three rankings agree (pairwise rank correlation 0.74–0.89). 3 of the four
attributes Ma et al. highlight (alcohol, sulphates, volatile acidity) are in the top four; citric acid ranks #6.
Higher alcohol, sulphates, citric acid go with better wine; higher volatile acidity with worse.

**How many lab tests are needed.** Random Forest was retrained on the top-k features, chosen
inside each training fold so the test folds never influence the choice:

| Subset | Features | Accuracy | Macro-F1 | Features chosen most often |
|---|---|---|---|---|
| top 1 (chosen in-fold) | 1 | 28.98 | 18.51 | alcohol |
| top 2 (chosen in-fold) | 2 | 58.93 | 32.65 | alcohol; volatile acidity |
| top 3 (chosen in-fold) | 3 | 66.25 | 36.77 | volatile acidity; sulphates; alcohol |
| top 4 (chosen in-fold) | 4 | 69.27 | 38.46 | volatile acidity; sulphates; alcohol; chlorides |
| top 6 (chosen in-fold) | 6 | 70.21 | 38.35 | volatile acidity; sulphates; alcohol; total sulfur dioxide; chlorides; density |
| top 8 (chosen in-fold) | 8 | 70.79 | 38.23 | volatile acidity; citric acid; chlorides; total sulfur dioxide; density; sulphates; alcohol; pH |
| top 11 (chosen in-fold) | 11 | 71.03 | 38.09 | fixed acidity; volatile acidity; citric acid; residual sugar; chlorides; free sulfur dioxide; total sulfur dioxide; density; pH; sulphates; alcohol |
| Ma et al.'s 4 key attributes | 4 | 67.55 | 37.68 | alcohol; sulphates; volatile acidity; citric acid |

### 6.5 Review 2 conclusion

Class balancing works as intended — rare-class recall and macro-F1 rise, at a stated cost in
accuracy. The Review-1 diagnosis held when tested, and fixing it without leakage improves the
paper's own ensemble. Three importance methods agree on what drives the prediction. None of
this approaches the paper's 89.73%: the best accuracy of any configuration is
71.03%, which strengthens rather than overturns the Review-1 conclusion.

<!-- REVIEW2-SECTION:END -->

## Appendix — Optional extension (not part of the reproduction)

An additional unsupervised analysis is included in
`src/novelty_cluster_mine_feedback.py`, runnable with `python run_all.py --with-novelty`.
It is coursework beyond the reproduction and is summarised here only briefly.

- **Clustering.** K-means and Ward's linkage over k=3..8 on the 11 attributes alone;
  best silhouette was K-means at k=3 (0.211), and clusters track quality only loosely.
  See `results/tables/cluster_quality_crosstab.csv`.
- **Outlier detection.** Isolation Forest and LOF both flag class 3 at roughly twice the
  rate of classes 5/6 (20.0% vs ~7-10%), suggesting those samples are genuinely atypical
  rather than merely few. Class 8 is method-dependent: most outlier-prone under Isolation
  Forest (33.3%), least under LOF (5.6%). See `results/tables/outlier_rates_by_class.csv`.
- **Cluster-ID feedback.** Adding the cluster label as a 12th feature did **not** help the
  classes it was aimed at: 3, 4 and 8 all changed by exactly 0.00. Elsewhere classes 5 and
  6 declined (−0.66 and −1.41) while class 7 rose 0.50. A negative result, reported as
  such. Note this comparison was produced by a 2-repeat smoke run rather than the 10-repeat
  canonical protocol, so its baseline column differs slightly from §4.2. See
  `results/tables/cluster_feedback_precision_comparison.csv`.
- **Association rule mining.** FP-Growth over tertile-binned features, filtered to
  `quality=High`, recovers all four attributes Ma et al. Figs. 4-5 flag as important
  (alcohol, sulphates, volatile acidity, citric acid) plus five others. See
  `results/tables/top_association_rules_overall.csv`.

---

## References

1. Ma, R., Mao, D., Cao, D., Luo, S., Gupta, S., & Wang, Y. (2024). From vineyard to
   table: Uncovering wine quality for sales management through machine learning.
   *Journal of Business Research*, 176, 114576.
   https://doi.org/10.1016/j.jbusres.2024.114576
2. Cortez, P., Cerdeira, A., Almeida, F., Matos, T., & Reis, J. (2009). Modeling wine
   preferences by data mining from physicochemical properties. *Decision Support
   Systems*, 47(4), 547–553. https://doi.org/10.1016/j.dss.2009.05.016
3. Cortez, P., Cerdeira, A., Almeida, F., Matos, T., & Reis, J. (2009). *Wine Quality*
   [Dataset]. UCI Machine Learning Repository.
   https://doi.org/10.24432/C56S3T · https://archive.ics.uci.edu/dataset/186/wine+quality
4. Pedregosa, F., Varoquaux, G., Gramfort, A., et al. (2011). Scikit-learn: Machine
   Learning in Python. *Journal of Machine Learning Research*, 12, 2825–2830.
5. Chawla, N. V., Bowyer, K. W., Hall, L. O., & Kegelmeyer, W. P. (2002). SMOTE: Synthetic
   minority over-sampling technique. *Journal of Artificial Intelligence Research*, 16,
   321–357. https://doi.org/10.1613/jair.953
6. Breiman, L. (2001). Random forests. *Machine Learning*, 45(1), 5–32.
   https://doi.org/10.1023/A:1010933404324
7. Wolpert, D. H. (1992). Stacked generalization. *Neural Networks*, 5(2), 241–259.
   https://doi.org/10.1016/S0893-6080(05)80023-1
8. Strobl, C., Boulesteix, A.-L., Zeileis, A., & Hothorn, T. (2007). Bias in random forest
   variable importance measures: Illustrations, sources and a solution. *BMC
   Bioinformatics*, 8, 25. https://doi.org/10.1186/1471-2105-8-25
9. Nadeau, C., & Bengio, Y. (2003). Inference for the generalization error. *Machine
   Learning*, 52(3), 239–281. https://doi.org/10.1023/A:1024068626366
