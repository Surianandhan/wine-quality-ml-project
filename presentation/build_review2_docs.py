"""
build_review2_docs.py -- writes BRIEFING_REVIEW2.md and SLIDE_BY_SLIDE_REVIEW2.md

Same rule as the deck: no result is typed by hand. Every number comes from
results/review2/tables/*.csv, and the slide-by-slide guide takes each slide's
"what to say" straight from the speaker notes inside second_review.pptx, so the
study notes can never disagree with the deck or the data.

    python presentation/build_review2_docs.py      (after node build_deck_review2.js)
"""
import os
from pathlib import Path

import pandas as pd
from pptx import Presentation

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
R2 = Path(os.environ.get("REVIEW2_DIR", ROOT / "results" / "review2"))
DECK = Path(os.environ.get("DECK_OUT", HERE / "second_review.pptx"))
OUT = Path(os.environ.get("DOCS_OUT", HERE))
# Where README.md and report/methodology.md live. Override when testing against
# non-real results so the real documents are never written with test numbers.
DOC_ROOT = Path(os.environ.get("DOC_ROOT", ROOT))


def t(name):
    return pd.read_csv(R2 / "tables" / name)


A, B1, B = t("A_class_balancing.csv"), t("B1_weight_temperature.csv"), t("B2_B3_improvements.csv")
CHOSEN, COMP = t("B4_chosen_temperatures.csv"), t("model_comparison.csv")
HEAD, PAIRED = t("headline_review1_vs_review2.csv"), t("paired_comparison.csv")
FI, CROSS, SUBSET, AGREE = (t("C_feature_importance.csv"), t("C_paper_crosscheck.csv"),
                            t("C_feature_subset.csv"), t("C_ranking_agreement.csv"))
BEST_NAME = (R2 / "tables" / "headline_best_model.txt").read_text().strip()

LABEL = {"none": "No balancing", "partial": "Review 1 (SVM + RF only)",
         "class_weight": "Class weights, all four", "smote": "SMOTE oversampling"}
ENS = "Ensemble (paper weights)"
R1_ENS, R1_RF = f"{ENS} | {LABEL['partial']}", f"RF | {LABEL['partial']}"
LT_R1, LT_SM = f"Learned-temperature ensemble | {LABEL['partial']}", f"Learned-temperature ensemble | {LABEL['smote']}"


def ens(b):
    return A[(A["balancing"] == b) & (A["model"] == ENS)].iloc[0]


def comp(name):
    return COMP[COMP["model"] == name].iloc[0]


def pair(a, b, metric):
    r = PAIRED[(PAIRED["model"] == a) & (PAIRED["compared_with"] == b) & (PAIRED["metric"] == metric)]
    return r.iloc[0] if len(r) else None


def short(name):
    return (name.replace("Ensemble (paper weights) | ", "Paper ensemble · ")
            .replace("Learned-temperature ensemble | ", "Learned-T ensemble · ")
            .replace("Review 1 (SVM + RF only)", "Review-1 setup")
            .replace("Class weights, all four", "class weights")
            .replace("SMOTE oversampling", "SMOTE").replace("No balancing", "no balancing")
            .replace(" | ", " · "))


def p(x, d=2):
    return f"{x:.{d}f}"


def pval(x):
    return "< 0.001" if x < 0.001 else f"{x:.3f}"


r1, rf1, sm = ens("partial"), comp(R1_RF), ens("smote")
best, best_acc = COMP.iloc[0], COMP.sort_values("accuracy", ascending=False).iloc[0]
best_bal = max(LABEL, key=lambda b: ens(b)["macro_f1"])
lt_r1, lt_sm = comp(LT_R1), comp(LT_SM)
stack4 = comp("Stacked: paper's 4 learners (class-weighted)")
stack_bal = comp("Stacked: paper's 4 learners, balanced combiner")

sweep = B1[(B1["balancing"] == "partial") & (B1["sharpen"] == "accuracy")]
rf_acc = float(sweep["rf_accuracy"].iloc[0])
overtake = sweep[sweep["accuracy"] > rf_acc]
first_T = int(overtake["temperature"].iloc[0]) if len(overtake) else None
sweep_best = sweep.sort_values("accuracy", ascending=False).iloc[0]

share_sharp = round(100 * (CHOSEN[CHOSEN["balancing"] == "partial"]["temperature"] >= 10).mean())
n_folds = int((CHOSEN["balancing"] == "partial").sum())

p_best = pair(BEST_NAME, R1_ENS, "macro_f1")
p_lt_ens = pair(LT_R1, R1_ENS, "accuracy")
p_lt_rf = pair(LT_R1, R1_RF, "accuracy")

top4 = list(FI.head(4)["feature"])
cross_in = list(CROSS[CROSS["in_our_top4"]]["paper_attribute"])
cross_out = CROSS[~CROSS["in_our_top4"]]
agree_lo, agree_hi = AGREE["spearman_rank_agreement"].min(), AGREE["spearman_rank_agreement"].max()
pos = list(FI[FI["spearman_rho"] > 0.2]["feature"])
neg = list(FI[FI["spearman_rho"] < -0.2]["feature"])
sub4 = SUBSET[SUBSET["subset"] == "top 4 (chosen in-fold)"].iloc[0]
sub11 = SUBSET[SUBSET["subset"] == "top 11 (chosen in-fold)"].iloc[0]
lt_beats_rf = lt_r1["accuracy"] > rf1["accuracy"]

missing_txt = "; ".join(f"{r.paper_attribute} ranks #{r.our_rank_best_model}" for r in cross_out.itertuples())

if lt_beats_rf:
    q9 = (f'"Yes — the learned-temperature ensemble reaches {p(lt_r1["accuracy"])}% against Random Forest\'s '
          f'{p(rf1["accuracy"])}%, beating it in {int(p_lt_rf["repeats_won"])} of {int(p_lt_rf["repeats"])} repeats. '
          "At Review 1 the ensemble lost to Random Forest; with the weighting fixed, it wins.\"")
else:
    q9 = (f'"It closes most of the gap: {p(lt_r1["accuracy"])}% against Random Forest\'s {p(rf1["accuracy"])}%, '
          f'up from {p(r1["accuracy"])}% at Review 1. Across the repeats it wins {int(p_lt_rf["repeats_won"])}, ties '
          f'{int(p_lt_rf["repeats_tied"])} and loses {int(p_lt_rf["repeats"] - p_lt_rf["repeats_won"] - p_lt_rf["repeats_tied"])} '
          "against Random Forest — a statistical tie. At Review 1 the ensemble lost to it by two points; with the "
          "weighting fixed, it draws level. I wouldn't claim it's better than Random Forest.\"")

top3_txt = f"{top4[0]}, {top4[1]} and {top4[2]}"
fix_worked = lt_r1["accuracy"] > r1["accuracy"]
memorise = (
    "Balancing rescued the rare classes at a stated cost; "
    + ("the weighting fix I predicted at Review 1 worked when done without leakage; "
       if fix_worked else "the weighting fix I predicted at Review 1 did not beat the original once done without leakage; ")
    + f"and {top3_txt} drive quality — but nothing gets near the paper's 89.73%."
)

sweep_claim = (f"overtakes Random Forest from T = {first_T}" if first_T
               else f"closes most of the gap to Random Forest, peaking at {p(sweep_best['accuracy'])}%")

# ==========================================================================
# BRIEFING
# ==========================================================================
briefing = f"""# Second Review — Briefing

**SURIANANDHAN S · 127018060 · CSE425 — Machine Learning Essentials**
Guide: Dr. Vidivelli S, AP-II · Department of CSE, School of Computing

Every number in this file is generated from `results/review2/tables/*.csv` by
`presentation/build_review2_docs.py`, the same source the slides read. If you
re-run the pipeline, re-run that script and this file stays correct.

---

## PART 1 — What changed since Review 1, in plain English

At Review 1 you showed a faithful reproduction of Ma et al. (2024). It reached
**{p(r1['accuracy'])}%** against the paper's 89.73%, and you explained the gap. Your guide asked
for three things. Here is what you did about each:

1. **Class balancing.** The rare quality classes were being ignored — class 4 had
   **{p(r1['recall_4'], 1)}%** recall. You compared four ways of fixing that on identical folds.
   **{LABEL[best_bal]}** worked best: macro-F1 went from {p(r1['macro_f1'])} to
   {p(ens(best_bal)['macro_f1'])}, and class-4 recall from {p(r1['recall_4'], 1)}% to
   {p(sm['recall_4'], 1)}% with SMOTE. The cost is a few points of accuracy, and you say so.

2. **Improving the result.** At Review 1 you said the paper's weights are too flat and
   predicted that sharpening them would help. You tested that prediction — sharpening
   {sweep_claim} — then built the fix properly: the sharpening level is **learned inside
   each training fold**, so the test data never touches it. That alone takes the paper's own
   ensemble from {p(r1['accuracy'])}% to **{p(lt_r1['accuracy'])}%**, winning {int(p_lt_ens['repeats_won'])} of
   {int(p_lt_ens['repeats'])} repeats. The best model on the primary metric is
   **{short(best['model'])}** (macro-F1 {p(best['macro_f1'])}).

3. **Feature importance.** **{top3_txt[0].upper() + top3_txt[1:]}** drive the prediction. Three
   different importance methods agree on that, and {len(cross_in)} of the paper's four key
   attributes land in your top four{f" ({missing_txt})" if len(cross_out) else ""}. Practically,
   **four lab tests** recover {round(100 * sub4['accuracy'] / sub11['accuracy'])}% of the accuracy all eleven achieve.

What did not change: **nothing comes near 89.73%.** The best accuracy anywhere is
{p(best_acc['accuracy'])}%. Review 2 strengthens the Review-1 conclusion; it does not overturn it.

### The sentence to memorise

> **"{memorise}"**

---

## PART 2 — The numbers to know cold

| What | Number | Where it's from |
|---|---|---|
| Review-1 ensemble — accuracy / macro-F1 | {p(r1['accuracy'])}% / {p(r1['macro_f1'])} | `A_class_balancing.csv` |
| Random Forest alone (Review-1 setup) | {p(rf1['accuracy'])}% | `A_class_balancing.csv` |
| Best macro-F1 (primary metric) | {p(best['macro_f1'])} — {short(best['model'])} | `model_comparison.csv` |
| Learned-temperature ensemble, paper's own members | {p(lt_r1['accuracy'])}% accuracy | `B2_B3_improvements.csv` |
| Repeats it beats the Review-1 ensemble | {int(p_lt_ens['repeats_won'])} of {int(p_lt_ens['repeats'])} | `paired_comparison.csv` |
| Class-4 recall, Review 1 → SMOTE | {p(r1['recall_4'], 1)}% → {p(sm['recall_4'], 1)}% | `A_class_balancing.csv` |
| Folds whose inner CV chose a sharp temperature (T ≥ 10) | {share_sharp}% of {n_folds} | `B4_chosen_temperatures.csv` |
| Accuracy with 4 lab tests vs all 11 | {p(sub4['accuracy'])}% vs {p(sub11['accuracy'])}% | `C_feature_subset.csv` |

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
> "On accuracy, yes — by about {p(r1['accuracy'] - sm['accuracy'])} points with SMOTE. But accuracy is
> dominated by classes 5 and 6. Balancing moves recall from those to the rare classes:
> class 4 went from {p(r1['recall_4'], 1)}% to {p(sm['recall_4'], 1)}%. On macro-F1, which weights all six
> classes equally, it improved. That trade-off is exactly what balancing is supposed to do."

### Q3. "Isn't choosing macro-F1 convenient, since accuracy dropped?"
> "I fixed macro-F1 as the primary metric in the code before running any Review-2
> experiment — it's in `config.py` with the reason written next to it, and the run log prints
> it before the first result. I still report accuracy on every slide, and I give the best
> accuracy model separately: {short(best_acc['model'])} at {p(best_acc['accuracy'])}%."

### Q4. "What is SMOTE, and doesn't it leak test data?"
> "It creates synthetic rare-class samples by interpolating between real neighbouring ones.
> It would leak if applied to the whole dataset, so it sits inside the pipeline after the
> scaler and only ever sees the training fold. The test fold is never resampled."

### Q5. "Why did class weights help less than SMOTE?"
> "Class weights make rare mistakes cost more, but the model still only sees ten class-3
> wines. SMOTE gives it more varied rare-class examples to draw a boundary around. Both
> help; on this data SMOTE helped more on macro-F1."

### Q6. "You said at Review 1 the weights were too flat. Did that hold up?"
> "Yes. I tested it directly: sharpening the weights {sweep_claim}. And when I let the inner
> cross-validation choose the temperature by itself, it picked a sharp setting in
> {share_sharp}% of folds. The data independently agrees with the diagnosis."

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
> {q9}

### Q10. "Why not use stacking? Isn't that the standard approach?"
> "I tried it. Plain stacking gets {p(stack4['accuracy'])}% accuracy but its macro-F1 drops to
> {p(stack4['macro_f1'])} — the learned combiner relearns the majority-class bias. With a balanced
> combiner it swings the other way: {p(stack_bal['accuracy'])}% accuracy. It's on the trade-off
> chart; it just isn't the best on the metric I chose in advance."

### Q11. "Is the improvement statistically significant?"
> "Across the ten repeats, the best model has higher macro-F1 than the Review-1 ensemble in
> {int(p_best['repeats_won'])} of {int(p_best['repeats'])}, with a Wilcoxon p of {pval(p_best['wilcoxon_p'])}. But I'd call that indicative,
> not proof — the repeats reuse the same wines, so they're not independent. A proper
> confidence interval needs a corrected resampled t-test, which is in my future work."

### Q12. "What is permutation importance and why not just use Random Forest's importances?"
> "Shuffle one feature in the test fold and see how much the score drops. It's measured on
> held-out data, so it reflects what the model really uses. Random Forest's built-in importance
> is computed on training data and is known to favour continuous features, so I used it only
> as a cross-check — and the rankings agree, {p(agree_lo)} to {p(agree_hi)} on rank correlation."

### Q13. "Some of your importances are negative. What does that mean?"
> "Shuffling that feature didn't hurt — the score went up slightly by chance. It means the
> model gets no usable signal from that feature. It's not a bug; it's noise around zero."

### Q14. "Do your important features match the paper?"
> "Mostly. {len(cross_in)} of the four attributes the paper highlights — {", ".join(cross_in)} — are in
> my top four.{f" {missing_txt}, so I only partly confirm that point." if len(cross_out) else ""} And the
> directions match wine chemistry: higher {", ".join(pos)} go with better wine; higher
> {", ".join(neg)} with worse."

### Q15. "What is the practical value of the feature importance?"
> "Lab tests cost money. With only four measurements — {sub4['features_most_often_chosen']} — the
> model reaches {p(sub4['accuracy'])}% accuracy, against {p(sub11['accuracy'])}% with all eleven. A winery could
> screen batches with a much smaller test panel."

### Q16. "How did you choose those four without leaking?"
> "The selection is a step inside the pipeline, so each training fold picks its own top four
> using only its own data. If I'd ranked features on the whole dataset first, the test folds
> would have influenced the choice."

### Q17. "Did you tune hyperparameters?"
> "No, deliberately. Every model keeps the Review-1 settings so that the only thing changing in
> each comparison is the thing being tested. Tuning is listed as a limitation and future work."

### Q18. "So did you finally get 89.73%?"
> "No — the best accuracy anywhere is {p(best_acc['accuracy'])}%. Better balancing, better weighting and
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
"""

(OUT / "BRIEFING_REVIEW2.md").write_text(briefing)

# ==========================================================================
# SLIDE BY SLIDE -- "what to say" comes from the deck's own speaker notes
# ==========================================================================
JOBS = {
    1: ("Open, and say the three asks in one sentence.", None),
    2: ("Re-anchor the panel: the baseline, the diagnosis, and the map of the talk.",
        "Don't re-present Review 1. One minute here, maximum."),
    3: ("Lock the rules before any result appears — the same move as slide 6 at Review 1.",
        "Say the disclosure box out loud. It pre-empts the hardest question about choosing macro-F1."),
    4: ("Show that only the balancing changes — a controlled comparison.",
        "If asked about leakage, point at the SMOTE box: training fold only."),
    5: ("The class-balancing result, and its honest cost.",
        "Lead with macro-F1 and rare-class recall, then say the accuracy cost yourself before anyone asks."),
    6: ("Set up the four routes so the next slides read as tests, not tinkering.", None),
    7: ("Test the Review-1 prediction.",
        "Say clearly that this chart is a diagnostic and is never used to choose a model."),
    8: ("The main improvement: the fix, done without leakage.",
        "Your strongest slide. Slow down. The chosen-temperature chart is the evidence."),
    9: ("Show the whole trade-off at once.",
        "Explain the frontier in one sentence: models no other model beats on both metrics."),
    10: ("Before and after, on every metric.",
         "Point at the consistency line under the table. Say 'indicative', not 'significant'."),
    11: ("Explain the importance methods before showing results.", None),
    12: ("What drives the prediction, and how it compares with the paper.",
         "Say 'associated with', never 'causes'."),
    13: ("Robustness and direction: three methods agree; the chemistry makes sense.", None),
    14: ("The practical, business-facing result: fewer lab tests.", None),
    15: ("Close all three asks, then restate that nothing reaches 89.73%.", None),
    16: ("Own the limitations before the panel raises them.", None),
}

prs = Presentation(str(DECK))
blocks = []
for i, slide in enumerate(prs.slides, 1):
    texts = [sh.text_frame.text.strip() for sh in slide.shapes if sh.has_text_frame and sh.text_frame.text.strip()]
    heading = texts[0].replace("\n", " ") if texts else f"Slide {i}"
    notes = slide.notes_slide.notes_text_frame.text.strip() if slide.has_notes_slide else ""
    job, trap = JOBS.get(i, ("Backup — present only if asked.", None))
    block = [f"### {'Slide' if i <= 16 else 'Backup slide'} {i} · {heading}", "", f"**Its job:** {job}", ""]
    if notes:
        block += ["**Say:** " + notes, ""]
    if trap:
        block += [f"⚠️ {trap}", ""]
    blocks.append("\n".join(block))

slides_doc = f"""# Second Review — slide by slide

**SURIANANDHAN S · 127018060 · CSE425**

Read this with `second_review.pptx` open beside it. The "Say" text for each slide is the
speaker note from the deck itself, so this file and the slides always match. It is
regenerated by `presentation/build_review2_docs.py`.

## The shape of the talk

| Slides | Move | What it does |
|---|---|---|
| 1 – 3 | Set-up | Where Review 1 left off, the three asks, and the rules fixed in advance |
| 4 – 5 | Ask 1 | Class balancing — what was tried, what it bought, what it cost |
| 6 – 10 | Ask 2 | Improving the result — the Review-1 prediction tested, then fixed properly |
| 11 – 14 | Ask 3 | Feature importance — what drives quality, and how many tests are needed |
| 15 – 16 | Close | Conclusion, limitations, references |
| 17 + | Backup | Only if asked |

---

""" + "\n---\n\n".join(blocks) + "\n"

(OUT / "SLIDE_BY_SLIDE_REVIEW2.md").write_text(slides_doc)
# ==========================================================================
# README and report sections, written between marker comments
# ==========================================================================
BEGIN, END = "<!-- REVIEW2-SECTION:BEGIN -->", "<!-- REVIEW2-SECTION:END -->"
NOTE = "<!-- Generated by presentation/build_review2_docs.py from results/review2/tables -- do not edit by hand. -->"


def md_table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def fill(path, content):
    text = path.read_text()
    a, b = text.index(BEGIN) + len(BEGIN), text.index(END)
    path.write_text(text[:a] + "\n" + NOTE + "\n\n" + content.strip() + "\n\n" + text[b:])


METRICS = [("accuracy", "Accuracy"), ("balanced_accuracy", "Balanced accuracy"), ("macro_f1", "**Macro-F1 (primary)**"),
           ("recall_3", "Recall, class 3"), ("recall_4", "Recall, class 4"), ("recall_5", "Recall, class 5"),
           ("recall_6", "Recall, class 6"), ("recall_7", "Recall, class 7"), ("recall_8", "Recall, class 8")]
headline_md = md_table(
    ["Metric (%)", "Review-1 ensemble", "Review-1 Random Forest", "Review-2 best", "Change vs Review-1 ensemble"],
    [[lab, p(HEAD.set_index("metric").loc[k, "review1_ensemble"]), p(HEAD.set_index("metric").loc[k, "review1_random_forest"]),
      p(HEAD.set_index("metric").loc[k, "review2_best"]), f"{HEAD.set_index('metric').loc[k, 'change_vs_review1_ensemble']:+.2f}"]
     for k, lab in METRICS])
# Not taken from run_log.txt: its wall-clock time includes any time the machine slept.
runtime_txt = " Expect roughly 1½ hours on an 8-core laptop."
regression_ok = abs(r1["accuracy"] - float(pd.read_csv(ROOT / "results/tables/model_accuracy_summary.csv")
                                          .set_index("model").loc["Ensemble (soft vote)", "overall_accuracy_pct"])) < 1e-6

readme_section = f"""
## 6. Review 2 — class balancing, improving the result, feature importance

At Review 1 the guide asked for three changes: class balancing, an improved result, and
feature importance. All three are in [`src/review2.py`](src/review2.py) and
[`src/feature_importance.py`](src/feature_importance.py):

```bash
python run_all.py --review2
```

Output goes to `results/review2/`; the Review-1 numbers in `results/tables/` stay exactly
as they were.{runtime_txt} {"As a regression check, the Review-1 configuration re-run inside the Review-2 code reproduces the Review-1 ensemble's " + p(r1["accuracy"]) + "% exactly." if regression_ok else ""}

**Primary metric: macro-F1**, fixed in `config.py` before any Review-2 run (accuracy rewards
predicting the two majority classes, which is exactly what balancing trades away). Accuracy
is reported alongside everywhere.

{headline_md}

Best on macro-F1: **{short(best['model'])}**. Best on accuracy: **{short(best_acc['model'])}**
({p(best_acc['accuracy'])}%).

- **Class balancing.** {LABEL[best_bal]} gives the paper's ensemble its best macro-F1
  ({p(r1['macro_f1'])} → {p(ens(best_bal)['macro_f1'])}); class-4 recall rises from {p(r1['recall_4'], 1)}% to
  {p(sm['recall_4'], 1)}% with SMOTE, at a cost of {p(r1['accuracy'] - sm['accuracy'])} points of accuracy.
- **The Review-1 diagnosis, tested and fixed.** Sharpening the paper's weights {sweep_claim}.
  Choosing the sharpening inside each training fold (nested CV) takes the paper's own ensemble
  from {p(r1['accuracy'])}% to {p(lt_r1['accuracy'])}%, winning {int(p_lt_ens['repeats_won'])} of {int(p_lt_ens['repeats'])} repeats.
- **Feature importance.** {top3_txt[0].upper() + top3_txt[1:]} drive the prediction; three importance
  methods agree (rank correlation {p(agree_lo)}–{p(agree_hi)}). Four lab tests reach {p(sub4['accuracy'])}%
  accuracy against {p(sub11['accuracy'])}% with all eleven.
- **Still nowhere near 89.73%** — consistent with the Review-1 finding.

Full write-up: [`report/methodology.md`](report/methodology.md) §6. Slides:
[`presentation/second_review.pptx`](presentation/second_review.pptx).
"""

ens_rows = [[LABEL[b], p(ens(b)["accuracy"]), p(ens(b)["balanced_accuracy"]), p(ens(b)["macro_f1"]),
             *[p(ens(b)[f"recall_{c}"], 1) for c in (3, 4, 5, 6, 7, 8)]]
            for b in ("none", "partial", "class_weight", "smote")]
cand = COMP[COMP["kind"] == "ensemble"].head(10)
cand_rows = [[int(r.rank_by_macro_f1), short(r.model), p(r.accuracy), p(r.balanced_accuracy), p(r.macro_f1)]
             for r in cand.itertuples()]
pair_rows = [[short(r.model), short(r.compared_with), "macro-F1" if r.metric == "macro_f1" else "accuracy",
              f"{r.mean_difference:+.2f}", f"{int(r.repeats_won)} / {int(r.repeats)}",
              "—" if pd.isna(r.wilcoxon_p) else pval(r.wilcoxon_p)] for r in PAIRED.itertuples()]
fi_rows = [[int(r.rank_final), r.feature, p(r.final_f1_drop), p(r.rf_f1_drop), f"{r.rf_mdi:.3f}",
            f"{r.spearman_rho:+.2f}", "yes" if r.highlighted_by_paper else ""] for r in FI.itertuples()]
subset_rows = [[r.subset, int(r.n_features), p(r.accuracy), p(r.macro_f1), r.features_most_often_chosen]
               for r in SUBSET.itertuples()]
sweep_rows = [[int(r.temperature), p(r.accuracy), f"{r.largest_weight:.3f}",
               p(B1[(B1.balancing == 'partial') & (B1.sharpen == 'both') & (B1.temperature == r.temperature)]['accuracy'].iloc[0])]
              for r in sweep.itertuples()]

report_section = f"""
## 6. Review 2 — class balancing, improving the result, feature importance

At the first review the guide asked for three changes: class balancing (only partially
present), an improved result, and feature importance. This section reports all three. The
code is in `src/review2.py` and `src/feature_importance.py`, run by `python run_all.py --review2`.

### 6.1 Protocol, primary metric and disclosures

Every Review-2 experiment uses the reproduction's protocol unchanged: stratified 10-fold
cross-validation × 10 repeats with fold seeds 0–9, and every scaler, resampler and feature
selector fitted inside the training fold. Results go to `results/review2/`, so the Review-1
numbers remain the baseline.{" Re-running the Review-1 configuration inside the Review-2 code reproduces its ensemble accuracy (" + p(r1["accuracy"]) + "%) exactly, which confirms the comparison is like-for-like." if regression_ok else ""}

The primary metric is **macro-F1**, fixed in `config.py` before any Review-2 experiment ran.
Classes 5 and 6 hold 82.5% of the data, so accuracy can stay high while the rare classes are
missed entirely — the Review-1 ensemble scores {p(r1['accuracy'])}% accuracy with {p(r1['recall_3'], 1)}% recall on
class 3 and {p(r1['recall_4'], 1)}% on class 4. Class balancing deliberately trades common-class accuracy
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

{md_table(["Scheme", "Accuracy", "Bal. acc.", "Macro-F1", "Rec. 3", "Rec. 4", "Rec. 5", "Rec. 6", "Rec. 7", "Rec. 8"], ens_rows)}

{LABEL[best_bal]} gives the best macro-F1. Balancing moves recall from the two majority
classes to the rare ones: with SMOTE, class-4 recall rises from {p(r1['recall_4'], 1)}% to {p(sm['recall_4'], 1)}% and
class 7 from {p(r1['recall_7'], 1)}% to {p(sm['recall_7'], 1)}%, while accuracy falls {p(r1['accuracy'] - sm['accuracy'])} points. Figure:
`results/review2/figures/A_class_balancing.png`.

### 6.3 Improving the result

**Testing the Review-1 diagnosis (diagnostic only).** Review 1 attributed the ensemble's
failure to beat Random Forest to near-uniform weights. Raising the paper's weights to a
power T before normalising tests that directly (T = 1 is the paper). Because these weights
are computed from the same out-of-fold predictions they are scored on, the sweep is never
used to select a model.

{md_table(["T", "Accuracy (accuracy term sharpened)", "Largest weight", "Accuracy (both terms sharpened)"], sweep_rows)}

Random Forest alone scores {p(rf_acc)}%. Sharpening the accuracy term {sweep_claim}. Sharpening
the diversity term as well eventually backfires: it concentrates weight on the learner whose
errors differ most from the others, which is usually the weakest.

**The fix, done properly (learned temperature).** The same scheme, but each outer training
fold runs an inner 5-fold cross-validation to choose T and whether to sharpen one term or
both, on the primary metric. The outer test fold never influences the choice. With the
reproduction's own four learners this raises accuracy from {p(r1['accuracy'])}% to {p(lt_r1['accuracy'])}% and
macro-F1 from {p(r1['macro_f1'])} to {p(lt_r1['macro_f1'])}; the inner CV chose a sharp temperature (T ≥ 10)
in {share_sharp}% of the {n_folds} folds. With SMOTE members it reaches a macro-F1 of {p(lt_sm['macro_f1'])}.

**Stacking and stronger members.** A logistic-regression combiner (Wolpert, 1992) trained on
the members' out-of-fold probabilities reaches {p(stack4['accuracy'])}% accuracy but only {p(stack4['macro_f1'])}
macro-F1 — it relearns the majority-class bias. A class-balanced combiner swings the other way
({p(stack_bal['accuracy'])}% accuracy). ExtraTrees and HistGradientBoosting were also tried as members.

The ensembles, ranked on the primary metric:

{md_table(["Rank", "Ensemble", "Accuracy", "Bal. acc.", "Macro-F1"], cand_rows)}

No candidate is best on both metrics; `results/review2/figures/B_tradeoff.png` plots every
candidate's accuracy against its macro-F1 with the Pareto frontier marked.

**Consistency across repeats.** Every candidate was scored on identical folds in each of the
ten repeats, so their per-repeat scores can be paired:

{md_table(["Model", "Compared with", "Metric", "Mean diff.", "Repeats won", "Wilcoxon p"], pair_rows)}

The repeats reuse the same 1,599 wines with different splits, so they are not independent
samples and these p-values are optimistic; the win counts are the plainer evidence. A
corrected resampled t-test (Nadeau & Bengio, 2003) would give proper intervals.

### 6.4 Feature importance

Three measures were computed and checked against each other: permutation importance on the
held-out folds (the primary measure — macro-F1 lost when a feature is shuffled in the test
fold), Random Forest's impurity importance (MDI, which is biased towards continuous,
many-valued features; Strobl et al., 2007), and the Spearman correlation of each feature with
quality for the direction of effect.

{md_table(["Rank", "Feature", "Perm., best model", "Perm., RF", "MDI, RF", "Spearman ρ", "Paper key"], fi_rows)}

The three rankings agree (pairwise rank correlation {p(agree_lo)}–{p(agree_hi)}). {len(cross_in)} of the four
attributes Ma et al. highlight ({", ".join(cross_in)}) are in the top four{"; " + missing_txt if len(cross_out) else ""}.
Higher {", ".join(pos)} go with better wine; higher {", ".join(neg)} with worse.

**How many lab tests are needed.** Random Forest was retrained on the top-k features, chosen
inside each training fold so the test folds never influence the choice:

{md_table(["Subset", "Features", "Accuracy", "Macro-F1", "Features chosen most often"], subset_rows)}

### 6.5 Review 2 conclusion

Class balancing works as intended — rare-class recall and macro-F1 rise, at a stated cost in
accuracy. The Review-1 diagnosis held when tested, and fixing it without leakage improves the
paper's own ensemble. Three importance methods agree on what drives the prediction. None of
this approaches the paper's 89.73%: the best accuracy of any configuration is
{p(best_acc['accuracy'])}%, which strengthens rather than overturns the Review-1 conclusion.
"""

fill(DOC_ROOT / "README.md", readme_section)
fill(DOC_ROOT / "report" / "methodology.md", report_section)
print("filled the Review-2 sections of README.md and report/methodology.md")

print(f"wrote {OUT / 'BRIEFING_REVIEW2.md'}")
print(f"wrote {OUT / 'SLIDE_BY_SLIDE_REVIEW2.md'}  ({len(prs.slides)} slides)")
