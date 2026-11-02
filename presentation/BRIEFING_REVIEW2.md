# Second Review — Briefing

**SURIANANDHAN S · 127018060 · CSE425 — Machine Learning Essentials**
Guide: Dr. Vidivelli S, AP-II · Department of CSE, School of Computing

Every number in this file is generated from `results/review2/tables/*.csv` by
`presentation/build_review2_docs.py`, the same source the slides read. If you
re-run the pipeline, re-run that script and this file stays correct.

---

## PART 1 — What changed since Review 1, in plain English

At Review 1 you showed a faithful reproduction of Ma et al. (2024). It reached
**69.01%** against the paper's 89.73%, and you explained the gap. Your guide asked
for three things. Here is what you did about each:

1. **Class balancing.** The rare quality classes were being ignored — class 4 had
   **0.6%** recall. You compared four ways of fixing that on identical folds.
   **SMOTE oversampling** worked best: macro-F1 went from 36.92 to
   39.34, and class-4 recall from 0.6% to
   26.4% with SMOTE. The cost is a few points of accuracy, and you say so.

2. **Improving the result.** At Review 1 you said the paper's weights are too flat and
   predicted that sharpening them would help. You tested that prediction — sharpening
   overtakes Random Forest from T = 25 — then built the fix properly: the sharpening level is **learned inside
   each training fold**, so the test data never touches it. That alone takes the paper's own
   ensemble from 69.01% to **70.89%**, winning 10 of
   10 repeats. The best model on the primary metric is
   **RF · SMOTE** (macro-F1 40.92).

3. **Feature importance.** **Alcohol, sulphates and volatile acidity** drive the prediction. Three
   different importance methods agree on that, and 3 of the paper's four key
   attributes land in your top four (citric acid ranks #6). Practically,
   **four lab tests** recover 98% of the accuracy all eleven achieve.

What did not change: **nothing comes near 89.73%.** The best accuracy anywhere is
71.03%. Review 2 strengthens the Review-1 conclusion; it does not overturn it.

### The sentence to memorise

> **"Balancing rescued the rare classes at a stated cost; the weighting fix I predicted at Review 1 worked when done without leakage; and alcohol, sulphates and volatile acidity drive quality — but nothing gets near the paper's 89.73%."**

---

## PART 2 — The numbers to know cold

| What | Number | Where it's from |
|---|---|---|
| Review-1 ensemble — accuracy / macro-F1 | 69.01% / 36.92 | `A_class_balancing.csv` |
| Random Forest alone (Review-1 setup) | 71.03% | `A_class_balancing.csv` |
| Best macro-F1 (primary metric) | 40.92 — RF · SMOTE | `model_comparison.csv` |
| Learned-temperature ensemble, paper's own members | 70.89% accuracy | `B2_B3_improvements.csv` |
| Repeats it beats the Review-1 ensemble | 10 of 10 | `paired_comparison.csv` |
| Class-4 recall, Review 1 → SMOTE | 0.6% → 26.4% | `A_class_balancing.csv` |
| Folds whose inner CV chose a sharp temperature (T ≥ 10) | 99% of 100 | `B4_chosen_temperatures.csv` |
| Accuracy with 4 lab tests vs all 11 | 69.27% vs 71.03% | `C_feature_subset.csv` |

---

## PART 3 — The concepts, simply

You will be asked what these words mean. One or two sentences each is enough.

**Class imbalance.** Classes 5 and 6 are 82.5% of the wines; class 3 has 10 wines and
class 8 has 18. A model can score high accuracy by mostly predicting 5 or 6 and never
learning the rare grades.

**Class weights (`class_weight='balanced'`).** Make a mistake on a rare-class wine cost more
during training. Each sample's weight is n_samples ÷ (n_classes × size of its class), so a
class-3 wine counts about 68 times as much as a class-5 wine. MLP and GradientBoosting have
no `class_weight` option, so you passed the same weights per sample — that is what the
`BalancedSampleWeight` wrapper in `review2.py` does.

**SMOTE.** Creates *synthetic* rare-class wines: pick a rare wine, pick one of its 5 nearest
rare neighbours, and create a new point somewhere on the line between them. Repeat until
every class is the same size. Reference: Chawla et al. (2002).

**Why SMOTE must sit inside the fold.** If you oversample the whole dataset first, synthetic
wines are built from test wines, and near-copies of test data leak into training. Your
pipeline does scale → SMOTE → fit inside each training fold; the test fold is never touched.
Same principle as the scaler bug you fixed at Review 1.

**Macro-F1.** Compute F1 (the balance of precision and recall) for each of the six classes
separately, then take the plain average. Every class counts equally, so it punishes a model
that ignores the rare grades. Accuracy does not.

**Balanced accuracy.** The average of the six per-class recalls. Same idea, simpler.

**Temperature / sharpening.** Raise each learner's weight to a power T before normalising.
T = 1 is the paper. Larger T makes the best learner's weight grow and the others shrink — a
"sharper" vote.

**Inner (nested) cross-validation.** To choose T without cheating, each outer training fold
runs its *own* 5-fold CV and picks the T that scores best there. The outer test fold is used
only once, at the very end, to score the result. That is why route 2 counts as a real result
and route 1 (the sweep) is only a diagnostic.

**Stacking.** Instead of hand-made weights, train a small model (logistic regression) that
takes the members' predicted probabilities as input and learns how to combine them.
Reference: Wolpert (1992).

**Permutation importance.** Shuffle one feature's column in the *test* fold — which breaks
its link to quality — and measure how much the score drops. A big drop means the model
relies on that feature. Done on held-out data, so it reflects real use.

**Impurity importance (MDI).** Random Forest's built-in importance: how much each feature
reduces impurity across all its splits. Free, but known to favour continuous, many-valued
features (Strobl et al., 2007). You used it only as a cross-check.

**Pareto frontier.** On the accuracy-vs-macro-F1 chart, the models that no other model beats
on *both* metrics at once. Anything off the frontier is strictly dominated.

---

## PART 4 — Viva questions and model answers

Answer in two beats: the direct answer, then the evidence. Then stop.

### Q1. "What did you change since Review 1?"
> "The three things you asked for. Class balancing — four schemes compared on identical
> folds. Improving the result — I tested my own Review-1 explanation and then fixed the
> weighting with a temperature learned inside each fold. And feature importance — permutation
> importance on held-out data, checked against two other methods."

### Q2. "Your accuracy went DOWN after balancing. Isn't that worse?"
> "On accuracy, yes — by about 5.15 points with SMOTE. But accuracy is
> dominated by classes 5 and 6. Balancing moves recall from those to the rare classes:
> class 4 went from 0.6% to 26.4%. On macro-F1, which weights all six
> classes equally, it improved. That trade-off is exactly what balancing is supposed to do."

### Q3. "Isn't choosing macro-F1 convenient, since accuracy dropped?"
> "I fixed macro-F1 as the primary metric in the code before running any Review-2
> experiment — it's in `config.py` with the reason written next to it, and the run log prints
> it before the first result. I still report accuracy on every slide, and I give the best
> accuracy model separately: RF · Review-1 setup at 71.03%."

### Q4. "What is SMOTE, and doesn't it leak test data?"
> "It creates synthetic rare-class samples by interpolating between real neighbouring ones.
> It would leak if applied to the whole dataset, so it sits inside the pipeline after the
> scaler and only ever sees the training fold. The test fold is never resampled."

### Q5. "Why did class weights help less than SMOTE?"
> "Class weights make rare mistakes cost more, but the model still only sees ten class-3
> wines. SMOTE gives it more varied rare-class examples to draw a boundary around. Both
> help; on this data SMOTE helped more on macro-F1."

### Q6. "You said at Review 1 the weights were too flat. Did that hold up?"
> "Yes. I tested it directly: sharpening the weights overtakes Random Forest from T = 25. And when I let the inner
> cross-validation choose the temperature by itself, it picked a sharp setting in
> 99% of folds. The data independently agrees with the diagnosis."

### Q7. "Why is the temperature sweep only a 'diagnostic'?"
> "Because in the sweep, the weights are computed from the same predictions they're scored on.
> Picking the best T from it would be choosing using test information. So I never use the
> sweep to pick a model — the learned-temperature version chooses T inside each training
> fold instead."

### Q8. "What is nested cross-validation?"
> "Cross-validation inside cross-validation. The outer loop gives the honest test score; the
> inner loop, run only on each outer training fold, makes any choices — here, the
> temperature. So the choice never sees the data it's scored on."

### Q9. "Does your improved ensemble beat Random Forest?"
> "It closes most of the gap: 70.89% against Random Forest's 71.03%, up from 69.01% at Review 1. Across the repeats it wins 4, ties 2 and loses 4 against Random Forest — a statistical tie. At Review 1 the ensemble lost to it by two points; with the weighting fixed, it draws level. I wouldn't claim it's better than Random Forest."

### Q10. "Why not use stacking? Isn't that the standard approach?"
> "I tried it. Plain stacking gets 70.92% accuracy but its macro-F1 drops to
> 34.96 — the learned combiner relearns the majority-class bias. With a balanced
> combiner it swings the other way: 59.20% accuracy. It's on the trade-off
> chart; it just isn't the best on the metric I chose in advance."

### Q11. "Is the improvement statistically significant?"
> "Across the ten repeats, the best model has higher macro-F1 than the Review-1 ensemble in
> 10 of 10, with a Wilcoxon p of 0.002. But I'd call that indicative,
> not proof — the repeats reuse the same wines, so they're not independent. A proper
> confidence interval needs a corrected resampled t-test, which is in my future work."

### Q12. "What is permutation importance and why not just use Random Forest's importances?"
> "Shuffle one feature in the test fold and see how much the score drops. It's measured on
> held-out data, so it reflects what the model really uses. Random Forest's built-in importance
> is computed on training data and is known to favour continuous features, so I used it only
> as a cross-check — and the rankings agree, 0.74 to 0.89 on rank correlation."

### Q13. "Some of your importances are negative. What does that mean?"
> "Shuffling that feature didn't hurt — the score went up slightly by chance. It means the
> model gets no usable signal from that feature. It's not a bug; it's noise around zero."

### Q14. "Do your important features match the paper?"
> "Mostly. 3 of the four attributes the paper highlights — alcohol, sulphates, volatile acidity — are in
> my top four. citric acid ranks #6, so I only partly confirm that point. And the
> directions match wine chemistry: higher alcohol, sulphates, citric acid go with better wine; higher
> volatile acidity with worse."

### Q15. "What is the practical value of the feature importance?"
> "Lab tests cost money. With only four measurements — volatile acidity; sulphates; alcohol; chlorides — the
> model reaches 69.27% accuracy, against 71.03% with all eleven. A winery could
> screen batches with a much smaller test panel."

### Q16. "How did you choose those four without leaking?"
> "The selection is a step inside the pipeline, so each training fold picks its own top four
> using only its own data. If I'd ranked features on the whole dataset first, the test folds
> would have influenced the choice."

### Q17. "Did you tune hyperparameters?"
> "No, deliberately. Every model keeps the Review-1 settings so that the only thing changing in
> each comparison is the thing being tested. Tuning is listed as a limitation and future work."

### Q18. "So did you finally get 89.73%?"
> "No — the best accuracy anywhere is 71.03%. Better balancing, better weighting and
> stronger members all improve things a little, but none comes near 89.73%. That supports
> what I showed at Review 1."

---

## PART 5 — Things NOT to say

| Don't say | Say instead |
|---|---|
| "Balancing improved accuracy." | "Balancing improved macro-F1 and rare-class recall; accuracy fell slightly." |
| "The improvement is statistically significant." | "It's consistent across the repeats — indicative, not a formal test." |
| "I chose macro-F1 because it looked better." | "I fixed macro-F1 in the code before running anything." |
| "The temperature sweep shows the best T is …" | "The sweep is a diagnostic; the real result chooses T inside each fold." |
| "SMOTE creates more data." | "SMOTE creates synthetic samples from the training fold only." |
| "Alcohol causes better wine." | "Higher alcohol is associated with higher quality in this data." |
| "The paper is wrong." | "I couldn't reproduce or reconcile the paper's 89.73%." |

That last one carries over from Review 1 and still matters most.

---

## PART 6 — Before the review

1. **Read Part 1 twice and say the memorised sentence out loud.** That is your opening.
2. Open `second_review.pptx` and read every speaker note aloud once. Time yourself:
   aim for 12–15 minutes for the 16 main slides.
3. Learn Part 2's table. When someone asks for a number, say it, then where it comes from.
4. Practise Q2, Q3, Q9 and Q11 out loud — those are the questions a careful examiner asks.
5. Know where the backup slides are. Each one answers a likely follow-up.
6. Bring `second_review.pdf` on a USB stick as a fallback.
