# First Review — Briefing

**SURIANANDHAN S · 127018060 · CSE425 Machine Learning Essentials**
**Guide: Dr. Vidivelli S, AP-II · Department of CSE, School of Computing**

> Read Part 1 five times. When you can say it in your own words without looking, you
> understand the project. Everything else in here is support.

---

## PART 1 — What this project actually is

### The problem, in one paragraph

Wine gets a quality score from 3 to 8. That score decides what the bottle sells for. But
the score is given by **three human experts tasting the wine** — slow, expensive, and a
matter of opinion. Separately, every winery already runs cheap lab tests on each batch:
how much alcohol, how acidic, how much sugar, and so on. Eleven such measurements.
**The question is simple: can the cheap lab numbers predict the expensive human verdict?**

### What a "reproduction study" is, and why it counts

In 2024 a group of researchers published a paper saying: yes, and we can do it **89.73%**
of the time. That is a very high claim for this dataset.

**A reproduction study means: take a published paper, build exactly what it describes, run
it, and report what you actually get.** It is normal, respected scientific work. Most
published machine learning results have never been independently re-run by anybody, and
when someone does re-run them the numbers often do not match. Finding *that*, and working
out *why*, is a real result — not a failure.

**You did not fail to get 89.73%. You built what they described, it gave 69.01%, and then
you worked out where their number comes from.** Those are two completely different
sentences, and the difference between them is the whole presentation.

### What you built

Four different prediction programs, each guessing the quality score from the eleven lab
numbers:

| Model | What it does, in one line |
|---|---|
| **SVM** | draws boundaries between the classes |
| **Random Forest** | hundreds of decision trees voting together |
| **Gradient Boosting** | a chain of trees, each new one fixing the previous ones' mistakes |
| **MLP** | a small neural network |

The paper used a different two for the last two slots — an **RNN** and an **ELM** — but both
are deep-learning-ish and this course is classical machine learning, so you swapped in the
closest classical equivalents. **The two most important ones, SVM and Random Forest, are
unchanged.**

Then the paper's clever bit: **combine all four into a committee**, where each member gets
a **vote weight** based on two things — how accurate it is, and how *different* its mistakes
are from everyone else's. A member who is wrong in the same places as everybody else adds
nothing new, so it gets a smaller vote.

To test it fairly, you split the data into ten parts, train on nine and test on the tenth,
rotate through all ten, then **repeat that whole thing ten times with different splits**.
A hundred training runs in total. Far more thorough than a single test.

### What you found — four things

**1. The committee got 69.01%. The paper said 89.73%.**

**2. Random Forest on its own — 71.03% — actually beat the committee.** That is the opposite
of what the paper claims. And you know why: the vote weights come out almost equal (each
about a quarter), so the "weighted committee" is really just a plain average. **Average one
strong player with three weaker ones and you land in the middle, not above the best one.**
That is arithmetic, not a bug in your code.

**3. Three separate checks explain the paper's number,** all done using numbers printed in
the paper itself:

- Their results table covers only **491 wines**, not all 1,599 — that looks like one small
  test, not the hundred-run test their text describes.
- Adding up the correct answers in their own table gives **82%**, not the 89.73% written in
  the text.
- Their own vote weights, applied to their own individual model scores, work out to about
  **67.5%**. Your 69.01% is **1.5 points** away from that. Their 89.73% is **22 points** away.

**4. A wording error in the paper.** They call their per-class measure "precision", but
their own worked example divides by the wrong total — it is actually **recall**. You proved
this by recomputing their table both ways: their published numbers only come out right one
way.

### The one thing you must never say

**Never say "the paper is wrong."** Say **"I could not reconcile these figures."**

You typed their confusion matrix by hand off a PDF page, and two of the six numbers do not
come out right — that might be *your* reading, not their mistake. **Saying that out loud is
what makes everything else you say believable.** A panel that hears you name your own weak
spot will trust your strong points.

### If you remember only one sentence

> **"It reproduced. The method ran exactly as published and gave 69.01%. What did not
> reproduce is the paper's reported number — and my project is the evidence for why."**

---

## PART 2 — The six numbers to memorise

Everything else you can read off the slide. These six you should know cold.

| Number | What it is |
|---|---|
| **89.73%** | what the paper reports |
| **69.01%** | what your reproduction gets |
| **71.03%** | Random Forest alone — beats your ensemble by 2.02 points |
| **491** | samples in the paper's results table (of 1,599) |
| **82.08%** | what the paper's own table diagonal actually gives |
| **0.3030** | the paper's largest weight — only 0.053 away from a uniform 0.25 |

---

## PART 3 — How to frame it (the most important part)

### The trap

If your story is `paper got 89.73% → I got 69.01% → here is why`, the panel hears
**"student couldn't get it working, then made excuses."** The explanation arrives *after*
they have already judged you, so it sounds like an alibi.

### The fix — say the number yourself, three times, on purpose

| Slide | What it does |
|---|---|
| **2 — Abstract** | You state the gap yourself, as the project's subject. A result you announce is a finding; a result dragged out of you is a confession. |
| **6 — Objectives** | You put your success criteria on screen *before* any result. The panel accepts them at minute four, so they judge 69.01% against *your* criteria, not against 89.73%. |
| **14 — Central finding** | Three independent checks. One reason is an excuse; three converging checks is a diagnosis. |

### Tone rules — non-negotiable

- Never say "the paper is wrong." Say "I could not reconcile these figures."
- Never apologise for 69.01%. Say it flat, like any other number.
- Do not say "unfortunately", "only", "just", or "we couldn't manage".
- Say "my reproduction reaches 69.01%" — **not** "I only got 69%".

---

## PART 4 — Viva questions and model answers

> **Answer in two beats.** Beat 1 = the direct answer in one sentence. Beat 2 = the
> evidence. **Then stop talking.** Over-explaining reads as nervousness; a short confident
> answer reads as mastery.

### Q1. "So your project just failed?"

> "No — the reproduction ran correctly and produced 69.01%. What did not reproduce is the
> paper's reported number, and finding out why is the project's contribution. I have three
> independent checks from the paper's own tables: their confusion matrix sums to 491 samples
> rather than the full 1,599; that same matrix's diagonal gives 82%, not the 89.73% the text
> states; and their own weights are never more than 0.053 from uniform, which applied to
> their own base accuracies implies about 67.5%. My 69.01% is 1.5 points from that. Tuning
> until I hit 89.73% would have been the actual failure."

**Never say:** "I ran out of time" · "maybe my code has a bug" · "I couldn't get it to work".

### Q2. "Why is your accuracy lower than the paper's?"

> "Three reasons, all from their own published tables. One, protocol: their Table 9 sums to
> 491 samples, about 31% of the dataset — a single hold-out split. Mine scores all 1,599
> samples ten times over, which is strictly harder. Two, arithmetic: the diagonal of that
> same table is 403 over 491, which is 82.08% — 7.65 points below what their text states.
> Three, mechanism: their weights are near-uniform, and applying them to their own base
> accuracies gives 67.52%, which is 1.49 points below my 69.01% and 22.21 below their 89.73%.
> Published accuracy for this six-class task is typically 62 to 72 percent, and mine is
> inside that band."

### Q3. "Are you claiming a published Elsevier paper is wrong?" ← the trap question

> "No, and I have been careful about this in the report. What I am saying is that I could not
> reconcile certain published figures with each other. I also have to declare a limitation of
> my own: I transcribed their Table 9 by eye from the printed PDF, and two of the six
> per-class values do not reproduce — most plausibly because of a reading error on my part.
> So the honest statement is 'these are figures I could not reconcile', not 'the paper is
> wrong'. If I could obtain the publisher's machine-readable table, that would settle it, and
> I have listed it as future work."

**If a panel member says it FOR you** — "sounds like the paper is wrong" — **do not agree.**
Say: *"I'd rather not go that far, sir/ma'am. I can only say I couldn't reconcile them, and
part of that may be my own transcription."*

### Q4. "Why does class 3 get 0%?"

> "Class 3 has ten samples out of 1,599. Under ten-fold cross-validation that is about one
> sample per test fold, so a model that ignores class 3 entirely loses almost nothing on
> overall accuracy — the loss function has no incentive to learn it. In my pooled confusion
> matrix the ensemble predicts class 3 only eight times across 15,990 predictions and gets
> none right; the true class-3 wines are mostly predicted as class 5. Cortez et al. also
> report 0% for class 3, so this is a known property of the dataset, not something specific
> to my implementation. I did not tune until it moved, because with ten samples any
> improvement would be noise. The proper fix is resampling — SMOTE or ADASYN — which is my
> first item of future work."

**Bonus if you are confident:** *"My outlier analysis supports this — both Isolation Forest
and LOF flag class 3 at about 20%, roughly twice the rate of classes 5 and 6, so those wines
are genuinely atypical, not just few."*

### Q5. "Why did you not use the actual RNN and ELM?"

> "The course is CSE425, Machine Learning Essentials, so deep-learning models are outside the
> syllabus. An RNN is a sequence model trained by backpropagation-through-time; the closest
> in-syllabus analogue to its iterative refinement is gradient boosting, where each new tree
> fits the residual errors of the trees before it. An ELM is a neural network whose hidden
> weights are random and frozen with a closed-form output layer — explicitly not
> backpropagation — so the closest classical analogue is a standard MLP. Importantly, SVM and
> Random Forest are unchanged, including Random Forest, which is the strongest member in both
> their run and mine. So the substitutions cannot explain the gap — the part of the ensemble
> doing the heavy lifting is identical."

### Q6. "What is your contribution if you only reproduced someone else's work?"

> "Four things. First, a leak-free, single-command reproducible implementation of a method
> whose code is not publicly available. Second, a three-check diagnosis of why the reported
> number does not reproduce, computed in code from the paper's own tables rather than just
> asserted. Third, a terminology correction — the paper labels its per-class metric
> 'precision', but its own Equation 14 divides by the actual-class total, which is recall; I
> verified it by recomputing their table both ways, and four of six values reproduce
> column-wise while only one of six reproduces row-wise. Fourth, Equation 1 is ambiguous
> about whether it is a soft or hard vote, so I implemented and reported both."

### Q7. "Why does your ensemble lose to Random Forest?" ← the question that separates grades

> "Because the weights come out almost uniform. Equation 5 normalises inverse errors and
> Equation 9 normalises pairwise error distances, and neither discriminates sharply when the
> base learners have broadly similar error rates. My measured weights span only 0.2356 to
> 0.2698 — a maximum deviation of 0.0198 from a uniform 0.25. With weights that flat, a
> weighted sum is effectively an unweighted average, and an average of one strong learner and
> three weaker ones necessarily lands between them, not above the strongest. That is exactly
> what I see: my ensemble beats three of its four members and trails Random Forest by 2.02
> points. And the paper's own Table 8 shows the same flatness — 0.3030 as its largest weight,
> only 0.053 from uniform — so this is a property of the scheme, not of my implementation."

### Q8. "What is the difference between soft and hard voting?"

> "Hard voting counts labels: each model votes for one class and the weighted majority wins.
> Soft voting averages probabilities: each model outputs a probability across all six classes,
> you take the weighted sum of those vectors, and predict the highest. Soft voting keeps the
> confidence information — a model that is 95% sure outweighs three models that are 40% sure —
> whereas hard voting throws that away. I implemented both because Equation 1 is a weighted
> sum and does not say whether ŷᵢ is a probability vector or a one-hot label. Soft gives
> 69.01%, hard gives 69.93%."

**Follow-up you MUST be ready for — "hard voting scored higher, so why is soft your headline?"**

> "Because soft voting is the literal reading of Equation 1 — an actual weighted sum of
> scores — and I fixed that as my headline before I saw the numbers, rather than picking
> whichever scored better afterwards. I report both, and I state explicitly in the report that
> soft voting scored lower."

**This is a strength. Deliver it with confidence, not apology.** Choosing the lower number on
principle is exactly the rigour your framing slide claims.

### Q9. "What is data leakage and where was it in your project?"

> "Data leakage is when information from the test set influences training, so your reported
> score is optimistic and won't hold on new data. In my project it was in the preprocessing.
> An earlier version min-max scaled the entire 1,599-row matrix once, then ran
> cross-validation on the scaled data. The minimum and maximum used for scaling were computed
> using test-fold rows, so every training fold had already seen information about its test
> fold. I fixed it by putting MinMaxScaler inside a scikit-learn Pipeline with the estimator,
> so the scaler is fit on the training fold only. All the numbers I presented are from the
> corrected version."

**Strong close:** *"I'd rather report the lower, correct number than the higher, leaked one."*

### Q10. "Why 10-fold cross-validation repeated 10 times? Why not a simple train-test split?"

> "Because the paper specifies ten runs of ten-fold cross-validation, and I wanted the
> protocol to match so the comparison is like-for-like. It is also the right choice here: with
> only ten class-3 samples, a single 80/20 split might put zero or four of them in the test
> set purely by luck, so the result would swing with the random seed. Repeating ten-fold CV
> ten times gives a hundred fold-runs and 15,990 pooled predictions, which averages that luck
> out. I use stratified folds so each fold preserves the class proportions."

### Q11. "Your confusion matrix sums to 15,990, but the dataset has 1,599 samples. Explain."

> "That is the ten repeats. Each repeat produces one out-of-fold prediction for every one of
> the 1,599 samples, and I pool all ten repeats before computing the confusion matrix — so
> 1,599 times ten is 15,990. Percentages are unaffected because numerator and denominator
> scale together. I pool rather than average per-fold scores so the rare classes contribute
> their actual counts instead of being averaged over folds where they happen to be absent."

### Q12. "What are the accuracy weight and the diversity weight, in plain terms?"

> "The accuracy weight is the normalised inverse of each learner's cross-validation error —
> fewer mistakes means a bigger weight. The diversity weight is about whether a learner makes
> *different* mistakes: for each learner you build a vector with a 1 where it got a sample
> wrong and 0 where it got it right, sum the Euclidean distances between that vector and every
> other learner's, and normalise. A learner whose errors overlap with everyone else's adds
> nothing new, so it gets less weight. The final weight is the average of the two. The idea is
> sound, but on this problem the normalisation flattens out the differences — which is my
> slide 14 finding."

### Q13. "Why balanced class weights on SVM and Random Forest but not the others?"

> "Because classes 3 and 8 have ten and eighteen samples, and without reweighting a model
> maximises accuracy by ignoring them. Scikit-learn's SVC and RandomForestClassifier both
> expose a class_weight parameter that scales each class's contribution to the loss inversely
> to its frequency, so I used it. GradientBoostingClassifier and MLPClassifier don't expose the
> same parameter directly, so I left them at defaults rather than implementing something the
> paper never describes. The paper states no imbalance handling at all, so this is my own
> explicit choice and I document it as such."

**If pressed — "isn't that inconsistent?"** → *"It is an asymmetry, yes, and a fair criticism.
The consistent alternative is per-sample weights for all four, and I have that noted."*

### Q14. "What is the business value? Why should a wine company care?"

> "The quality score that drives a wine's price and shelf placement is set by a three-person
> sensory panel, which is slow, expensive and subjective. The eleven physicochemical attributes
> come from routine lab tests a winery already runs. If you can predict the score from the lab
> tests, you can screen a batch before it goes to a tasting panel, flag likely-premium batches
> early, and support pricing at scale. That is why the paper is in the Journal of Business
> Research rather than a pure ML venue. My honest assessment is that at 69% exact-match
> accuracy over six classes it is a screening aid, not a replacement for the panel — but it is
> well above the 2009 baseline on the two classes holding 82% of the data."

### Q15. "How do I know your code is correct?"

> "Three ways. One, everything runs from a single command, `python run_all.py`, and every
> number in this presentation is written to a CSV by that command — nothing is typed in by
> hand. Two, the random seeds are fixed, zero through nine, so it reproduces exactly on re-run.
> Three, the checks against the paper are themselves in code, in evaluate.py — the Table 9
> reconciliation reads the paper's printed numbers from config.py and recomputes them, so you
> can inspect the arithmetic rather than take my word for it. I also have a Jupyter notebook
> that walks the pipeline cell by cell."

**If they push — "reproduces on YOUR machine, or anywhere?"** You have measured this, so answer
with the evidence:

> "I tested it across environments. On a different Python version and a different scikit-learn
> version, SVM and MLP come out identical to sixteen decimal places. Random Forest and gradient
> boosting drift by under two tenths of a point, because the tree implementations changed
> between scikit-learn releases. The ranking order, the ensemble still trailing Random Forest,
> and the gap against the paper — none of those change. So the conclusions are reproducible
> even where the last decimal place is not, and I pin the exact versions in requirements.txt."

That answer is stronger than a flat "yes, it reproduces", because it shows you know *which*
parts of a result are stable and which are not — which is the actual subject of your project.

### Q16. "Can you run it right now?"

> "Yes — two ways. On this laptop it takes about thirty seconds for the reduced protocol.
> Or I can open it in Google Colab in a browser, which rebuilds the whole project from
> scratch — it downloads the dataset, writes the source files, and runs the pipeline. I do
> not need my own machine for it."

Have the Colab notebook already open in a browser tab before you walk in. If the panel says
yes, you click `Runtime → Run all` rather than fumbling with a laptop. See
[`../HOW_TO_RUN.md`](../HOW_TO_RUN.md) §4b.

### Three more they may throw in

**"Why not merge classes into good/bad and get 90%?"**
> "That is a different and much easier problem — binary classification on this dataset
> routinely exceeds 90%. But the paper reports all six classes, and merging would make my
> comparison meaningless. I chose the harder like-for-like comparison deliberately."

**"What was the hardest part?"**
> "Realising my first version had data leakage in the preprocessing. My scores dropped when I
> fixed it, which was uncomfortable, but the corrected numbers are the real ones."

**"What would you do differently?"**
> "Two things. Build the statistical testing in from the start rather than reporting point
> estimates, and try to obtain the paper's table in machine-readable form early so the
> transcription caveat wouldn't exist."

---

## PART 5 — Things NOT to say

| Do not say | Say instead |
|---|---|
| "The paper is wrong" / "their numbers are impossible" | "Figures I could not reconcile" |
| "62–72% is the published range" *(if pushed for citations)* | "That's the range I saw across the papers in my literature survey; I haven't compiled a formal citation table and will tighten it before the next review." **Do not invent citations.** |
| "Equations 5 and 9 are flawed" | "On this problem, with four learners of similar error rates, those equations produce near-uniform weights." |
| "Soft voting was better on the minority classes" *(plural)* | "Soft voting recovered some class-4 samples where hard voting recovered none — though that is 3 correct predictions out of 530, so I would not over-read it." |
| Anything about silhouette scores or lift, unprompted | Keep the unsupervised work on backup slide 3. It is not your contribution and invites questions on work you don't need to defend. |

---

## PART 6 — 48-hour plan

**Day 1**
1. Read Part 1 five times, until you can say the one sentence cold.
2. Open the deck and read every speaker note aloud once.
3. Memorise the six numbers in Part 2.
4. Run `python run_all.py` once so you have watched the pipeline execute with your own eyes —
   you will likely be asked "did you run this yourself?"

**Day 2**
1. Rehearse **slide 14 out loud, ten times**, including the caveat box. It is the hardest two
   minutes of the talk.
2. Rehearse **Q1, Q3, Q6, Q7 and Q9** out loud — those five are where the marks move.
3. Practise the two-beat discipline: direct answer, evidence, **stop**.
4. Full run-through with a timer. Target 12 minutes for slides 1–16.

**Morning of**
- Re-read Part 3. Walk in knowing that **69.01% is your finding, not your failure.**

---

## Where everything lives

| What | Where |
|---|---|
| The deck | `presentation/first_review.pptx` (16 slides + 4 backup, speaker notes on every slide) |
| Deck generator | `presentation/build_deck.js` — re-run with `node build_deck.js` if a number changes |
| Full written report | `report/methodology.md` |
| Every number on every slide | `results/tables/*.csv` |
| The headline chart | `results/figures/accuracy_comparison.png` |
| Run everything | `python run_all.py` |
