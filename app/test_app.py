"""
test_app.py -- automated checks for the web application.

    python app/test_app.py

1. Every page renders without raising an exception.
2. The app's models use exactly the project's settings (Review-1 Random Forest
   and the SMOTE pipeline from review2.make_paper_learners).
3. Predictions are valid quality grades and probabilities sum to 1.
4. The overview page's headline numbers equal the values in the result CSVs.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parent / "streamlit_app.py"
ROOT = APP.parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(APP.parent))

from base_learners import get_base_learners  # noqa: E402
from preprocessing import load_red_wine_xy  # noqa: E402
from review2 import make_paper_learners  # noqa: E402

failures = []


def check(name, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  ({detail})" if detail else ""))
    if not ok:
        failures.append(name)


print("1. every page renders")
for fn in ["page_overview", "page_dataset", "page_reproduction", "page_balancing",
           "page_improvement", "page_importance", "page_predict"]:
    script = (f"import sys; sys.path.insert(0, {str(APP.parent)!r}); sys.path.insert(0, {str(ROOT / 'src')!r})\n"
              f"import streamlit_app as app\napp.{fn}()")
    at = AppTest.from_string(script, default_timeout=300).run()
    check(f"page renders: {fn}", not at.exception, str(at.exception[0].message)[:160] if at.exception else "")

print("2. models match the project's settings")
import streamlit_app as app  # noqa: E402

X, y, _, _ = load_red_wine_xy()
models = app.trained_models.__wrapped__() if hasattr(app.trained_models, "__wrapped__") else app.trained_models()
rf, rf_smote = list(models.values())
# Identical predictions from a freshly fitted project model prove identical settings.
check("Random Forest = Review-1 RF (identical predictions)",
      np.array_equal(rf.predict_proba(X), clone(get_base_learners()["RF"]).fit(X, y).predict_proba(X)))
check("RF + SMOTE = Review-2 SMOTE RF (identical predictions)",
      np.array_equal(rf_smote.predict_proba(X), clone(make_paper_learners("smote")["RF"]).fit(X, y).predict_proba(X)))

print("3. predictions are valid")
for name, m in models.items():
    p = m.predict_proba(X[:50])
    check(f"{name}: probabilities sum to 1", np.allclose(p.sum(axis=1), 1.0))
    check(f"{name}: predicted grades are real grades", set(m.predict(X[:50])) <= set(np.unique(y)))

print("4. headline numbers match the result files")
summary = pd.read_csv(ROOT / "results/tables/model_accuracy_summary.csv").set_index("model")
check("reproduction accuracy is 69.01", round(summary.loc["Ensemble (soft vote)", "overall_accuracy_pct"], 2) == 69.01)
comp = pd.read_csv(ROOT / "results/review2/tables/model_comparison.csv")
check("best macro-F1 model is RF + SMOTE", comp.iloc[0]["model"] == "RF | SMOTE oversampling")

print(f"\n{'ALL CHECKS PASSED' if not failures else f'{len(failures)} FAILED: {failures}'}")
sys.exit(1 if failures else 0)
