# How to run this project

**SURIANANDHAN S · 127018060 · CSE425 — Machine Learning Essentials**

Everything below was run and timed on this Mac on 22 Sep 2026. If a command is in a
box, it works as written.

---

## 0. The one thing that will trip you up

The project folder and its Python environment are in **two different places**:

```
/Users/AIRUS/Documents/ML Essentials/          <- the environment lives HERE
├── .venv/                                       Python 3.11.15 + every package
└── wine-quality-ml-project/                   <- the code lives HERE
    ├── run_all.py                               the single entry point
    ├── src/                                     the six modules
    ├── data/raw/                                winequality-red.csv
    ├── results/{tables,figures}/                the numbers on your slides
    ├── report/methodology.md                    the full write-up
    └── presentation/                            deck, briefing, PDF
```

If you just open Terminal and type `python run_all.py`, you get your **Anaconda** Python
(3.13.9), not the project's. The core run happens to still work there, but it is not the
interpreter the results were produced with, and `--with-novelty` crashes outright.

**Always activate the environment first.** Everything else follows from that.

---

## 1. From a cold Terminal to results — copy this whole block

```bash
cd "/Users/AIRUS/Documents/ML Essentials"
source .venv/bin/activate
cd wine-quality-ml-project
python run_all.py --quick
```

Line by line:

1. Go to the folder that holds the environment.
2. **Activate it.** Your prompt changes to show `(.venv)` — that is how you know it worked.
3. Go into the project.
4. Run it.

Once `(.venv)` is showing, plain `python` is the right Python and you can run any command
in the next section.

To leave the environment afterwards: `deactivate`.

---

## 2. The commands

| Command | What it does | Time | Writes to |
|---|---|---|---|
| `python run_all.py --quick` | 10-fold CV × **2** repeats. A sanity pass. | **29 s** (measured) | `results/_quick_run/` |
| `python run_all.py` | 10-fold CV × **10** repeats = 100 fold-runs. **This is the real protocol** and produces the numbers on your slides. | ~2 min | `results/tables/`, `results/figures/` |
| `python run_all.py --with-novelty` | The above **plus** the optional clustering / outlier / association-rule extension. | ~3 min | same, plus extra files |
| `python run_all.py --help` | Lists the flags. | instant | — |

**You do not need to run any of these before the review.** All the canonical results are
already sitting in `results/` and every number in your deck comes from them. Running
`python run_all.py` again regenerates the same numbers (the random seed is fixed at 42),
so it is safe — just unnecessary.

### Why `--quick` is safe and the full run is the one that counts

`--quick` uses 2 repeats instead of 10, so its numbers are slightly different — RF comes
out at 71.45% instead of 71.03%. Those are **not** the numbers on your slides. To make
sure a fast sanity pass can never silently replace the real ones, `--quick` writes to a
separate `results/_quick_run/` folder that is git-ignored. Verified just now: after
running `--quick`, the canonical `results/tables/model_accuracy_summary.csv` still had its
original timestamp, untouched.

---

## 2b. Review 2 — class balancing, improvements, feature importance

```bash
python run_all.py --review2
```

This runs the reproduction first, then the three Review-2 experiments your guide asked for.
Expect **roughly 1½ hours** on this Mac (8 cores) — it fits several thousand models, some
with nested cross-validation. Start it with the charger plugged in and stop the Mac from
sleeping: a sleeping Mac pauses the run, and a flat battery loses it.

| What | Where it goes |
|---|---|
| Every Review-2 table | `results/review2/tables/` |
| Every Review-2 figure | `results/review2/figures/` |
| The full console output, with timing | `results/review2/run_log.txt` |
| Review-1 numbers | `results/tables/` — regenerated identically, **unchanged** |

For a faster check that the code runs, `python run_all.py --quick --review2` uses 2 repeats
and writes to `results/_quick_run/review2/` instead.

Two things in the log are worth knowing. The line
`Regression check vs Review 1: ... -> MATCH` proves the Review-2 code reproduces your
Review-1 ensemble to every digit. The `Paired comparison` block shows how many of the 10
repeats each improvement wins.

---

## 3. Where the numbers on your slides come from

Every figure you will say out loud traces to a CSV you can open in front of the panel.

| Slide | What it claims | Open this file |
|---|---|---|
| **12** Results: ranking | RF 71.03 · Ensemble-hard 69.93 · Ensemble-soft 69.01 · GradBoost 67.67 · SVM 61.95 · MLP 61.35 | `results/tables/model_accuracy_summary.csv` |
| **13** Results: per-class | The bar chart, and Cortez / Ma / ours per quality class | `results/figures/accuracy_comparison.png` and `results/tables/benchmark_comparison.csv` |
| **14** Central finding | 491 samples · 30.71% · 403 correct · 82.08% · 7.65-point discrepancy | `results/tables/paper_table9_reconciliation.csv` |
| **14** Central finding | max weight deviation 0.053 · implied 67.52% · their gap 22.21 · ours 1.49 | `results/tables/paper_internal_consistency_check.csv` |
| **B1** backup | Confusion matrices | `results/tables/confusion_matrix_*.csv` |
| **B2** backup | Full per-class precision / recall / F1 | `results/tables/metrics_*.csv` |
| **B4** backup | Which of the paper's per-class values reproduce | `results/tables/paper_table9_per_class_check.csv` |

To show one on screen:

```bash
open results/tables/model_accuracy_summary.csv
```

That opens it in Numbers or Excel. For a quick look without leaving Terminal, use
`cat results/tables/model_accuracy_summary.csv`.

---

## 4. If the panel asks you to run it live

Have Terminal already open and already in the project with `(.venv)` showing. Then:

```bash
python run_all.py --quick
```

It finishes in **under 30 seconds** and prints the model ranking, the per-class comparison
against the published benchmarks, the ensemble weights, and both reconciliation tables.

While it runs, say something like:

> "This is the reduced protocol — two repeats instead of ten, so it finishes in half a
> minute. It writes to a separate folder so it can't overwrite the ten-repeat results my
> slides quote. The full run is the same code with ten repeats and takes about two minutes."

Do **not** run the full `python run_all.py` in front of them. Two minutes of silence is a
long time in a review.

---

## 4b. Running it in Google Colab (no laptop needed)

`notebooks/wine_quality_colab.ipynb` runs the whole project in a browser. Nothing to
install, no Google Drive to mount, no GitHub repo — it rebuilds the project inside Colab
from scratch.

**To use it:**

1. Go to [colab.research.google.com](https://colab.research.google.com)
2. `File` → `Upload notebook` → pick `notebooks/wine_quality_colab.ipynb`
3. `Runtime` → `Run all`

That's it. It downloads the dataset from UCI, writes the project's real source files to
disk, runs the pipeline, and displays the figure and result tables inline.

**Why this is worth having for the review:** it does not depend on your laptop, your
Python environment, or the college PC. Any machine with a browser and a Google account
can run it. If your laptop dies on the morning of the review, this is your fallback.

### Three things to know

**It has no internet dependency beyond Colab itself.** The dataset download is the only
network call, and if it fails the notebook falls back to a copy of the CSV embedded
inside the notebook. Either way it verifies it parsed 1,599 rows × 12 columns before
continuing. A bad Wi-Fi connection in the review room cannot break the demo.

**It runs `--quick` by default.** Colab's free tier gives you 2 CPU cores, against the
several your Mac has, so the full 10-repeat protocol takes roughly 5–10 minutes there.
The quick pass exercises exactly the same code path. To run the full protocol, change
`!python run_all.py --quick` to `!python run_all.py` in section 5.

**It shows the real source code.** Sections 4's cells use `%%writefile`, so the actual
contents of `config.py`, `preprocessing.py`, `base_learners.py`, `ensemble.py`,
`evaluate.py` and `run_all.py` are visible in the notebook. If an examiner asks to see
the implementation, scroll — you are not asking them to take anything on trust.

### Do not edit this notebook by hand

It is generated from your real source files by a script. If you edit `src/` and then
hand-edit the notebook to match, the two will drift apart. Regenerate instead:

```bash
python notebooks/build_colab_notebook.py
```

That reads `src/*.py` and `run_all.py`, re-embeds them, and rewrites the notebook. It is
correct by construction.

---

## 4c. Is this reproducible? (measured, not assumed)

This was tested properly, because "is your work reproducible?" is a viva question and a
vague answer invites follow-ups.

**Same environment, re-run:** bit-for-bit identical. The full 10-repeat protocol was run
in a completely fresh directory with a freshly downloaded dataset, and every figure came
back matching `results/tables/` to all 16 decimal places — RF `71.03189493433396`,
soft-vote ensemble `69.01188242651656`, and so on.

**Different Python and different scikit-learn:** conclusions identical, last decimals not.
Running the same protocol on Python 3.14 / scikit-learn 1.7.2 / NumPy 2.5 instead of
Python 3.11 / scikit-learn 1.9.0 / NumPy 2.4 gave:

| Model | Slides (sklearn 1.9.x) | sklearn 1.7.2 | Drift |
|---|---|---|---|
| SVM | 61.951219512195124 | 61.951219512195124 | **identical to 16 digits** |
| MLP | 61.350844277673545 | 61.350844277673545 | **identical to 16 digits** |
| Random Forest | 71.03 | 71.21 | +0.18 |
| GradBoost | 67.67 | 67.75 | +0.09 |
| Ensemble (hard) | 69.93 | 69.97 | +0.04 |
| Ensemble (soft) | **69.01** | **69.17** | +0.16 |

Only the two tree ensembles move, because scikit-learn changed those implementations
between releases. **Nothing that matters changes:** the ranking order is the same, the
ensemble still trails Random Forest, and the gap against the paper's 89.73% is the same
to within two tenths of a point.

That is a *good* answer to give a panel — it shows you know which parts of a result are
stable and which are not, which is the actual subject of your project. The model answer is
in [`presentation/BRIEFING.md`](presentation/BRIEFING.md) Q15.

**To guarantee an exact match**, use the pinned versions in `requirements.txt` — which is
what the `.venv` already has.

---

## 4d. A change made to your Anaconda install — please read

While testing the Colab notebook, a cell ran `pip install mlxtend`. In Colab that is
harmless. On this Mac the notebook's shell escape resolved `python` to
`/opt/anaconda3/bin/python` rather than the project venv, so the install landed in your
**Anaconda environment** and changed two things there:

| Package | Before | After |
|---|---|---|
| scikit-learn | 1.7.2 | **1.9.1** (upgraded as an mlxtend dependency) |
| mlxtend | not installed | **0.25.0** |

**Your project is unaffected.** The `.venv` was not touched, `results/` was not touched,
and the canonical numbers are unchanged. Anaconda 1.9.1 is also *closer* to the project's
pinned 1.9.0 than 1.7.2 was, so if anything the change helps.

It was left in place rather than reverted, because downgrading would be a second
unrequested change to your environment and carries more risk than the first. If you would
rather put it back exactly as it was:

```bash
/opt/anaconda3/bin/python -m pip install "scikit-learn==1.7.2" && /opt/anaconda3/bin/python -m pip uninstall -y mlxtend
```

The notebook no longer has this failure mode — it now invokes `sys.executable` (its own
interpreter), quoted, so it can never reach into a different install.

---

## 5. The notebook — for walking through it step by step

`notebooks/reproduction_walkthrough.ipynb` runs the same pipeline cell by cell, which is
easier to narrate than a wall of Terminal output.

```bash
jupyter lab notebooks/reproduction_walkthrough.ipynb
```

(JupyterLab 4.4.7 and Notebook 7.4.5 are both installed in the venv.) It opens in your
browser. Run cells with **Shift + Enter**.

The notebook uses a 2-repeat protocol and writes to `notebooks/_scratch_outputs/` — same
protection as `--quick`, so it can't touch your canonical results either.

If you'd rather open it in VS Code: open the file, then pick the interpreter at
`/Users/AIRUS/Documents/ML Essentials/.venv/bin/python` as the kernel. If you pick the
Anaconda one instead, the imports will work but you're running a different scikit-learn
than the results were produced with.

---

## 6. Rebuilding the presentations

Only needed if you want to change a slide.

```bash
cd presentation
node build_deck.js
```

This regenerates `first_review.pptx` from `build_deck.js`. Node v24.14.0 and the
`pptxgenjs` dependency are already installed locally in `presentation/node_modules/`.

**The build reads `results/figures/accuracy_comparison.png`** — slide 13 embeds it
directly. If that file is ever deleted, regenerate it with `python run_all.py` before
rebuilding the deck.

The PDF (`first_review.pdf`) is a manual export, not rebuilt by that command. Keep it on
your USB stick as a fallback in case the college PC mangles the .pptx.

### The Review-2 deck and study notes

```bash
cd presentation
node build_deck_review2.js
python build_review2_docs.py
```

The first command builds `second_review.pptx`. It reads **every number from
`results/review2/tables/`** — nothing is typed in by hand — so after a re-run of
`--review2`, rebuilding the deck updates every slide automatically.

The second writes `BRIEFING_REVIEW2.md` and `SLIDE_BY_SLIDE_REVIEW2.md` (the slide guide's
"what to say" is taken from the deck's own speaker notes) and refreshes the Review-2 sections
of `README.md` and `report/methodology.md`. Run it after the deck.

**Open the Review-1 deck in PowerPoint, not Keynote or Google Slides.** Its two native
charts (slides 9 and 12) come out blank in Keynote. The Review-2 deck uses image charts only,
so it looks the same everywhere.

---

## 6b. Rebuilding the report and the conference paper

Both Word files are generated from the result files, so they never disagree with them:

| File | Built by |
|---|---|
| `report/Project_Report_127018060.docx` | `report/build_report.py` |
| `report/Conference_Paper_127018060.docx` | `report/build_paper.py` |

```bash
cd "/Users/AIRUS/Documents/ML Essentials/wine-quality-ml-project"
"../.venv/bin/python" report/build_figures.py
/opt/anaconda3/bin/python report/build_report.py --pages
/opt/anaconda3/bin/python report/build_paper.py --render
```

- `build_figures.py` draws the report's extra figures and the web-app examples (project venv).
- The two builders need `python-docx` and `pandoc` (both already in Anaconda) — see
  `report/requirements-docs.txt`.
- `--pages` opens the report in Pages, reads off the page of every heading, figure and table,
  and writes those page numbers into the contents, figure and table lists. In Word you can
  also refresh them yourself: select all, then F9.
- The layout comes from `report/templates/` — empty copies of the sample report and paper
  (styles, margins, numbering and footers only; none of the sample's text).
- **After deploying the app**, put the two links into `APP_URL` and `REPO_URL` at the top of
  `report/tools/results.py` and run the commands again; every "[... added after deployment]"
  placeholder is replaced.

## 7. What each source file does

Useful if a panel member points at the screen and asks "what does this do?"

| File | Its job |
|---|---|
| `run_all.py` | The only entry point. Loads the data, runs Step 3 (the reproduction), optionally Step 4, prints everything. |
| `src/config.py` | Every constant in one place — paths, the 10×10 protocol, the seed (42), and the published numbers from Ma et al. and Cortez et al. that we compare against. |
| `src/preprocessing.py` | Loads `winequality-red.csv` into X (11 features) and y (quality 3–8). |
| `src/base_learners.py` | The four base learners — SVM, Random Forest, MLP, Gradient Boosting — each wrapped in a scikit-learn `Pipeline` with the scaler **inside** it. That is what prevents data leakage. |
| `src/ensemble.py` | The paper's Equations (1)–(9): the accuracy weight, the diversity weight, their average, and both the soft and hard weighted votes. Also drives the 10-fold × 10-repeat loop. |
| `src/evaluate.py` | Confusion matrices, per-class metrics, the bar chart, and the two reconciliation analyses against the paper's own printed tables. |
| `src/review2.py` | Review 2: the four class-balancing schemes, the weight-sharpening test, the learned-temperature fix, stacking, and the paired comparison across repeats. |
| `src/feature_importance.py` | Review 2: permutation importance on held-out folds, impurity importance, direction of effect, and the "how many lab tests" experiment. |
| `src/novelty_cluster_mine_feedback.py` | The optional extension. Not part of the reproduction; appendix material only. |

---

## 8. When something goes wrong

**`ModuleNotFoundError: No module named 'mlxtend'`**
You're on Anaconda's Python, not the project's. Run `source "/Users/AIRUS/Documents/ML Essentials/.venv/bin/activate"` and try again. Check for `(.venv)` in your prompt.

**`can't open file 'run_all.py'`**
You're in the wrong folder. `cd "/Users/AIRUS/Documents/ML Essentials/wine-quality-ml-project"`.

**`FileNotFoundError: ... winequality-red.csv`**
The dataset moved. It belongs at `data/raw/winequality-red.csv`; re-download it from the
UCI link in the README if it's gone.

**The numbers came out different from my slides.**
You ran `--quick` and are reading `results/_quick_run/` instead of `results/tables/`. The
slides quote the 10-repeat numbers in `results/tables/`.

**`ImportError: cannot import name '_safe_tags'` when running `--review2`**
An old `imbalanced-learn` (0.12.x) is installed; it does not work with scikit-learn 1.9.
Fix: `python -m pip install "imbalanced-learn==0.14.2" "scikit-learn==1.9.0"`.

**Deck build says `missing figure: ...` or a CSV is not found**
The Review-2 run has not finished, or was interrupted. Re-run `python run_all.py --review2`.

**Deck build says `Cannot find module 'pptxgenjs'`**
Run `npm install` inside `presentation/` first.

---

## 9. Two things not to do

1. **Don't delete `results/`.** Those CSVs are the evidence behind every number you will
   say out loud, and the deck build reads a figure from that folder.
2. **Don't run the full `python run_all.py` five minutes before the review** just to check
   it still works. Use `--quick`. It exercises exactly the same code path in 29 seconds.
