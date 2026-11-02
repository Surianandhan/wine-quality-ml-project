# Slide-by-slide walkthrough

**SURIANANDHAN S · 127018060 · CSE425 — First Review**

Read this with `first_review.pptx` open beside it. Every slide already has the same
guidance as a speaker note inside PowerPoint — this file is for rehearsing away from the
laptop.

---

## The shape of the argument

The deck is not 16 separate topics. It is one argument in four moves. If you understand
the four moves, you can recover any slide even if you lose your place.

| Slides | Move | What it does |
|---|---|---|
| **1–4** | **Setup** | Here is the problem, here is the paper I reproduced, here is why it was worth reproducing |
| **5–8** | **Method** | Here is their method, here is where I followed it, here is where I had to decide |
| **9–11** | **Build** | Here is the data, the architecture, and the protocol — including a bug I found in my own code |
| **12–16** | **Payoff** | Here is what it produced, here is why it differs from the paper, here is what that teaches |

**The single most important structural fact:** you disclose the 69.01 vs 89.73 gap
yourself on **slide 2**, before anyone can ask. A result you announce is a finding. A
result someone extracts from you is a confession. This is why slide 2 exists.

---

## Act 1 — Setup (slides 1–4)

### Slide 1 · Title

**Its job:** establish who you are and what this is, in ten seconds.

On screen: the project title, your name and register number, CSE425, Dr. Vidivelli S,
Department of CSE.

**Say:** "Good morning. My project is a reproduction study of a 2024 *Journal of Business
Research* paper on predicting wine quality from laboratory measurements using an ensemble
of machine learning models. I re-implemented their method under our classical machine
learning syllabus and compared what it actually produces against what they report."

Note the phrase **"compared what it actually produces against what they report."** That
sentence sets up everything. Don't drop it.

---

### Slide 2 · The project in 30 seconds ◄ **CRITICAL**

**Its job:** state the result — including the gap — before anyone asks.

On screen: three big numbers. **89.73%** (reported by the paper) · **69.01%** (our
reproduction) · **3 checks** (explain the gap). Then five bullets: the task, the base
paper, this work, what the project actually is, and the contribution.

**Say:** "Here is the whole project on one slide, including the result, so nothing is a
surprise later. The paper reports 89.73 percent. My implementation of the same method
reaches 69.01 percent. The project is not an attempt to close that gap by tuning — it is
an investigation into where the gap comes from, and I resolve it using three independent
checks computed from the paper's own tables."

**Slow down here.** This is the most important 20 seconds of the presentation. If a panel
member is going to form an opinion of you, it forms here. Deliver it as a finding you are
proud of, not an apology.

---

### Slide 3 · Problem statement

**Its job:** make the panel care about the problem before you show them any method.

On screen: two panels — **the expensive signal** (a three-sommelier tasting panel scores
quality 3–8; slow, costly, subjective) versus **the cheap signal** (11 chemical tests the
winery already runs). Then why it matters commercially, the ML question, and why it's hard.

**Say:** "The score that decides a wine's price is assigned by a human tasting panel, which
is slow and expensive. The chemical tests are cheap and objective. So the question is
whether the cheap measurements can predict the expensive judgement. The difficulty is that
almost the entire dataset sits in two of the six quality levels, so the rare grades are
very hard to learn."

That last sentence is load-bearing — it is the reason your class 3, 4 and 8 numbers are
low, and you have now explained it at minute two rather than defending it at minute ten.

---

### Slide 4 · Literature survey

**Its job:** show the paper's number is unusual — which is what made it worth reproducing.

On screen: a three-row table. Cortez et al. (2009) with the standard per-class baseline ·
Ma et al. (2024) at 89.73% and +9.02 over their best base learner · this work at 69.01%
plus a diagnosis.

**Say:** "Cortez and colleagues introduced this dataset in 2009 and their per-class results
are the standard baseline. Ma and colleagues in 2024 built a weighted ensemble on top of it
and reported 89.73 percent, which is a very high figure for this task. The commonly
reported range for this exact six-class problem is roughly 62 to 72 percent, so that number
stood out, and that is part of why I chose this paper to reproduce."

⚠️ **If asked which papers give the 62–72% band:** say it is the range you saw across the
papers in your literature survey, that you have **not** compiled a formal citation table
for it, and that you will tighten it before the next review. **Do not invent citations.**
An examiner who catches a fabricated reference will distrust everything else you said.

---

## Act 2 — Method (slides 5–8)

### Slide 5 · The base paper's method

**Its job:** prove you understand the method well enough to have rebuilt it from equations.

On screen: the four base learners (SVM, RNN, ELM, Random Forest), then the weighting
scheme — `wᵢ = ½(w_accuracy + w_diversity)`, Eq. (4). The accuracy weight is the normalised
**inverse** of CV error. The diversity weight builds a 0/1 error vector per learner and
sums Euclidean distances to the others. Combine with Eq. (1): `ŷ = Σ wᵢŷᵢ`. A side panel
shows the paper's own Table 8 weights: SVM 0.2516 · RNN 0.2286 · ELM 0.2168 · **RF 0.3030**.

**Say:** "Their idea is that a learner should be trusted for two reasons: it is accurate,
and it makes different mistakes from the others. The accuracy weight is the normalised
inverse of the cross-validation error, so fewer mistakes means more weight. The diversity
weight measures how far each learner's pattern of mistakes sits from the others. The final
weight is the average of the two, and the ensemble is the weighted sum."

**Plant the number:** the slide says *"Remember 0.3030 — it returns on slide 14."* Say it
out loud. It is the most important number after 89.73, and when it reappears the panel
will feel the argument close.

---

### Slide 6 · Objectives and success criteria ◄ **CRITICAL**

**Its job:** get the panel to accept your definition of success **before** they see 69.01%.

On screen: four objectives, then a boxed **"This project is successful if:"** — every
component implemented as written, the evaluation leak-free and re-runnable, and whatever
number the method produces reported as-is with discrepancies investigated rather than
tuned away. Then a line in red: *"It is NOT successful if we reach 89.73% by changing the
protocol until the number moves."*

**Say:** "These are my objectives and, below them, the criteria I set for calling the
project successful. I want to be explicit about the third one, because it decides how you
should read my results slide: the goal was to implement the method faithfully and report
what it produces, not to chase a target number. If I had tuned the protocol until it hit
89.73 percent, that would have been the failure mode, not the success."

This slide is the hinge of the whole deck. The panel agrees to these criteria at minute
four, so at minute nine they judge 69.01% against *these*, not against 89.73%. Do not rush
it and do not skip the red line.

---

### Slide 7 · Existing system vs. proposed system

**Its job:** show you made deliberate engineering decisions, not accidental ones.

On screen: a five-row comparison. Base learners · scaling (theirs: min-max, timing
unstated; yours: inside a Pipeline, fit per training fold) · class imbalance (theirs: not
stated; yours: balanced class weights) · reading of Eq. (1) (theirs: ambiguous; yours:
both implemented) · verification (theirs: —; yours: their tables reconciled in code).

**Say:** "The left column is what the paper specifies; the right is what I built. Two
learners were substituted for syllabus reasons, which I cover next. The other three rows
are places where the paper is silent or ambiguous, and instead of guessing quietly I made
the choice explicit and, where the paper was genuinely ambiguous, implemented both
readings."

The bottom line — *"Where the paper is silent or ambiguous, I made the choice explicit
rather than guessing quietly"* — is a sentence that marks you as someone doing research
rather than following a tutorial.

---

### Slide 8 · Syllabus substitutions ◄ **pre-empts the obvious attack**

**Its job:** kill the question "aren't your substitutions the reason for the gap?" before
it is asked.

On screen: a four-row table. SVM — **unchanged**. Random Forest — **unchanged**. RNN →
GradientBoosting (each new tree fits the residual errors of the previous ones — the
in-syllabus analogue of iterative refinement). ELM → MLPClassifier (closest analogue that
is still a neural net, but trained by standard backpropagation).

**Say:** "Two of the four learners are outside a classical-ML syllabus, so I substituted
them. A recurrent network refines its state step by step, and gradient boosting is the
classical analogue: each new tree fits the errors the previous trees made. An extreme
learning machine is a neural net whose hidden weights are random and frozen, so the closest
in-syllabus analogue is a standard MLP trained by backpropagation."

Then, **deliberately**, the box at the bottom: "SVM and Random Forest are untouched —
including Random Forest, which is the strongest learner in both the paper and my run. So
the substitutions cannot be what explains the gap."

Slow down on that last sentence. It closes off an entire line of attack.

---

## Act 3 — Build (slides 9–11)

### Slide 9 · Dataset

**Its job:** make the class imbalance *visible*, so your low rare-class numbers are already
explained when they appear.

On screen: a bar chart of class counts — 3:10 · 4:53 · 5:681 · 6:638 · 7:199 · 8:18. Then:
classes 5 and 6 are 82.5% of the data; classes 3 and 8 together are 1.75%; under 10-fold CV
that is about **one class-3 sample per test fold**; no class dropped or merged.

**Say:** "This is the same 1,599-sample red wine dataset the paper uses. The imbalance is
the defining property: classes five and six are over eighty percent of the data, while
class three has ten samples and class eight has eighteen. Under ten-fold cross-validation
that is about one class-three sample per test fold. I kept all six classes rather than
merging them into good and bad, because the paper reports all six and I wanted the
comparison to be like-for-like."

The "one sample per test fold" line is the single most effective defence you have for
class 3 scoring 0.00.

---

### Slide 10 · System architecture

**Its job:** show the whole pipeline as one picture, and point at the leak-free detail.

On screen: CSV in → stratified 10-fold CV × 10 repeats = 100 fold-runs → four learners,
each wrapped in `Pipeline([MinMaxScaler → estimator])` → 0/1 error vector per learner →
`w_accuracy` + `w_diversity` → `wᵢ = ½(w_acc + w_div)` → Eq. (1) in two readings (soft:
`Σ wᵢ·Pᵢ`, hard: `Σ wᵢ·onehot(ŷᵢ)`) → pooled confusion matrix, per-class metrics,
reconciliation.

**Say:** "This is the full pipeline. Data comes in, and everything inside the dashed box
happens once per fold, a hundred times in total. The four learners each produce out-of-fold
predictions; from those I build a zero-one error vector per learner, which feeds both the
accuracy weight and the diversity weight. Those combine into the final weight, and the
weighted sum gives the ensemble prediction. The critical detail is that the scaler lives
inside the pipeline, so it only ever sees the training fold."

---

### Slide 11 · Implementation and protocol ◄ **do not skip for time**

**Its job:** this is where you earn marks for engineering maturity. It contains the bug
you found in your own code.

On screen: the stack and single entry point (`python run_all.py`) · the protocol (stratified
10-fold × 10 repeats, seeds 0–9, 100 fold-runs, **15,990 pooled predictions**) · balanced
class weights as your own explicit choice · both readings of Eq. (1) · every number written
to `results/tables/*.csv` by that one command, nothing typed by hand.

Then a highlighted box: **"No data leakage — a bug I found and fixed in my own code."** An
earlier version min-max scaled all 1,599 rows once and *then* cross-validated, so the
scaling constants were computed using test-fold rows. Moving `MinMaxScaler` inside the
Pipeline fixed it — **and lowered the scores.**

**Say:** "Everything runs from a single command, and every number I show you is written to
a CSV by that command, so it is re-runnable. The most important implementation detail is
the box at the bottom: the scaler sits inside the pipeline so it only sees training data.
An earlier version of my code scaled the whole dataset before cross-validation, which leaks
information from the test folds into the scaling constants and inflates the accuracy. I
found that, fixed it, and my scores went down — the numbers you are about to see are the
corrected, honest ones."

Examiners reward a student who found their own bug and accepted a worse number for it far
more than one who reports a high number. **If you are running short on time, cut slide 19,
not this one.**

---

## Act 4 — Payoff (slides 12–16)

### Slide 12 · Results — model ranking

**Its job:** show the ranking honestly, and drop the clue that explains it.

On screen: a horizontal bar chart — MLP 61.35 · SVM 61.95 · GradBoost 67.67 · **Ensemble
(soft) 69.01** · Ensemble (hard) 69.93 · **Random Forest 71.03**. A callout reads
**−2.02 points: our ensemble vs Random Forest.** Then: the ensemble beats 3 of its 4
members but trails RF; the paper reports the opposite (+9.02 over their best); and measured
weights span only **0.2356–0.2698**, a maximum deviation of **0.0198** from a uniform 0.25.

**Say:** "Random Forest is the strongest single model at 71.03 percent. My ensemble reaches
69.01 percent, which beats three of its four members but sits two points below Random
Forest. The paper reports the opposite — their ensemble is nine points above their best
member. The last line is the clue that explains it: my computed weights barely move away
from a uniform quarter each, and I come back to that in two slides."

That forward reference matters. It tells the panel the anomaly is *about to be explained*,
so they hold the question instead of interrupting.

---

### Slide 13 · Results — per class ◄ **the headline figure**

**Its job:** show that the *shape* of the paper's result reproduces even though the numbers
don't.

On screen: the bar chart (blue = Cortez 2009, orange = Ma 2024, green = yours) plus the
table:

| Class | Cortez | Ma | Ours |
|---|---|---|---|
| 3 | 0.00 | 33.33 | 0.00 |
| 4 | 20.00 | 63.16 | 0.57 |
| 5 | 67.50 | 84.80 | **81.66** |
| 6 | 57.70 | 88.06 | 69.87 |
| 7 | 58.60 | 77.08 | 49.90 |
| 8 | 0.00 | 50.00 | 11.11 |
| **Overall** | — | **89.73** | **69.01** |

**Say:** "This is the headline figure. Blue is the 2009 baseline, orange is the paper, green
is mine. The qualitative shape reproduces exactly: the two well-populated middle classes
are predicted well and the rare extreme classes are the hardest, which is the paper's own
conclusion. On class five I am within about three points of them. Class 4 at 0.57 percent
is 53 samples sitting directly between the two dominant classes, so it gets absorbed by
them — that is the imbalance problem and it is my first item of future work."

Then the separate finding: "The paper labels this metric *precision*, but their own worked
example divides by the actual class total, which is *recall*. I verified that by recomputing
their table both ways."

That terminology correction is a genuine contribution. It says you read the paper closely
enough to check its arithmetic, not just its prose.

---

### Slide 14 · Why 89.73% does not reproduce ◄ **CRITICAL — the payoff**

**Its job:** convert a weak-looking result into a diagnosis. Everything has been building
to this slide.

On screen: three numbered checks, all computed **from the paper's own printed tables**.

1. **Protocol mismatch** — their Table 9 confusion matrix sums to **491** samples, 30.7% of
   1,599. That is a single hold-out split, not the 100-run cross-validation the text
   describes. Yours scores all 1,599 samples ten times over.
2. **Internal arithmetic** — the diagonal of that same table is **403 of 491 = 82.08%**,
   which is **7.65 points below** the 89.73% stated in the paper's own text.
3. **The weights are flat** — their Table 8 weights are never more than **0.053** from a
   uniform 0.25. Applied to their *own* base accuracies they give **67.52%**.

Then the comparison strip: weighted average of the paper's own base accuracies = **67.52%**
· our reproduction **69.01%**, **+1.49** above it · the paper's reported **89.73%**,
**+22.21** above it.

And the mechanism: *with weights this flat, a weighted sum ≈ an unweighted average — which
lands BETWEEN its members, never above the strongest.*

**Say:** "Three independent checks, all computed in code from the paper's own printed
tables. First, their confusion matrix sums to 491 samples, about thirty percent of the
dataset, which looks like a single hold-out split rather than the hundred-run
cross-validation the text describes. Second, the diagonal of that same table gives 82
percent, not the 89.73 the text states. Third, and this is the mechanism: their own weights
are never more than 0.053 away from a uniform quarter, and applying their weights to their
own base accuracies gives 67.5 percent — my result sits one and a half points above that,
theirs sits twenty-two points above it."

⚠️ **Then deliver the caveat clearly — do not mumble it:**

"I want to be clear that I transcribed that confusion matrix by eye from the PDF, so two of
six values may be reading errors on my part. I am reporting this as figures I could not
reconcile, not as a claim that the paper is wrong."

**The caveat is what makes the other three claims credible.** A student who overclaims gets
taken apart. A student who states the limit of their own evidence gets believed. Never say
"the paper is wrong" — say "I could not reconcile these figures."

---

### Slide 15 · Conclusion

**Its job:** name what succeeded and what didn't, and extract the general lesson.

On screen: two panels — **"Structurally the reproduction succeeded"** (all four base
learners, Eqs. 1 and 4–9, min-max preprocessing, the 10×10 protocol, all as specified)
versus **"Numerically it did not"** (69.01% against 89.73%, ensemble doesn't overtake RF).
Then, in bold: **"The gap is diagnosed, not excused."** Then the methodological lesson, and
four contributions.

**Say:** "My summary is that the reproduction succeeded structurally and did not reproduce
numerically, and the second part is the informative one. Everything the paper specifies was
implemented as written. The methodological lesson is that when you normalise weights across
four learners with broadly similar error rates, the weights come out nearly uniform, and a
nearly uniform weighted sum is just an average — which lands between your models, not above
your best one. That is a general property of the scheme, not something specific to my code."

That last sentence — *a general property of the scheme, not specific to my code* — is your
strongest defensive line in the entire deck. It moves the finding from "my implementation
underperformed" to "here is a limitation of the published method."

Your four contributions: (1) a leak-free single-command reproducible implementation, (2) a
three-check diagnosis from the paper's own tables, (3) the terminology correction, (4) both
readings of an ambiguous Eq. (1) implemented and compared.

---

### Slide 16 · Future work and references

**Its job:** show you know what you'd do next — and that one of those things is a test of
your own explanation.

On screen, future work: SMOTE/ADASYN or cost-sensitive loss for classes 3, 4, 8 · paired
t-test or Wilcoxon across the 100 fold-runs for confidence intervals · **weight sharpening
— add a temperature to Eqs. (5) and (9) to test the flat-weight diagnosis directly** ·
repeat on the 4,898-sample white wine set (already in `data/raw/`) · obtain the publisher's
machine-readable Table 9 to remove the transcription caveat. Then the four references.

**Say:** "The most direct next step is handling the imbalance properly with resampling,
because that is what limits classes three, four and eight. The second is statistical testing
across my hundred fold-runs so I can report confidence intervals rather than point
estimates. The third is the most interesting: deliberately sharpening the weights to test my
own explanation — if the flat-weight diagnosis is right, sharpening them should let the
ensemble overtake Random Forest. Thank you, I am happy to take questions."

The weight-sharpening item is the best single line in your future work, because it proposes
a **falsifiable test of your own claim**. That is what a researcher does.

---

## Backup slides (17–20) — only if asked

Do not present these. They exist so that when a panel member asks a hard question, you jump
to a slide instead of talking.

| Slide | Pull it out when… | What it shows |
|---|---|---|
| **17** Confusion matrices | "Show me the confusion matrix" / "prove the class-3 result" | Pooled soft-vote and RF matrices over 15,990 predictions. Row sums are 10× the class counts because predictions pool across 10 repeats. Class 4 at 0.57% is literally **3 correct out of 530**; class 8 at 11.11% is **20 out of 180**. |
| **18** Full per-class metrics | "What about precision, not just the paper's metric?" | Conventional precision / recall / specificity for every model. The paper's "precision" is numerically the **recall** row. |
| **19** Unsupervised extension | Only if asked about extra work | Clustering, outlier detection, cluster-ID feedback (a **negative result** — no improvement on classes 3, 4, 8), FP-Growth rules recovering all four attributes the paper highlights. |
| **20** Table 9 reconciliation | "Show me the reconciliation arithmetic" | Per-class recomputation: **4 of 6 reproduce column-wise** (3 exactly), only 1 of 6 row-wise. Column-wise = TP ÷ actual-class total = recall, confirming the terminology finding empirically. |

**On slide 19, be brief if you go there at all.** Discussing silhouette scores or lift
invites questions about work that is not your contribution. The honest framing is: "That was
an optional extension behind a flag. The cluster-ID feedback produced no improvement on the
target classes — I report it as a negative result."

---

## If you remember nothing else

Three slides carry the presentation:

- **Slide 2** — you announce the gap yourself.
- **Slide 6** — the panel accepts your success criteria before seeing any result.
- **Slide 14** — three independent checks turn the gap into a diagnosis.

And one sentence:

> **"It reproduced. The method ran exactly as published and gave 69.01%. What did not
> reproduce is the paper's reported number — and my project is the evidence for why."**

The 15 viva questions with model answers are in [`BRIEFING.md`](BRIEFING.md) Part 4.
