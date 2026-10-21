# Putting the web app online

About 10 minutes. You need a GitHub account; Streamlit Community Cloud signs in with it.

## 1. Check the app runs on your Mac

```bash
cd "/Users/AIRUS/Documents/ML Essentials/wine-quality-ml-project"
"../.venv/bin/python" -m streamlit run app/streamlit_app.py
```

It opens at http://localhost:8501. Stop it with `Ctrl + C`.

Optional — the automated checks (every page renders, models match the project):

```bash
"../.venv/bin/python" app/test_app.py
```

## 2. Put the project on GitHub

1. Go to https://github.com/new
2. Repository name: **wine-quality-ml-project** · **Public** · do **not** add a README
3. Click **Create repository**
4. In Terminal, run these one at a time (replace `YOUR-USERNAME`):

```bash
cd "/Users/AIRUS/Documents/ML Essentials/wine-quality-ml-project"
git init
git add .
git commit -m "Wine quality prediction: reproduction, Review 2 and web app"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/wine-quality-ml-project.git
git push -u origin main
```

**Before pushing, confirm the paper PDF is not included** — it is a copyrighted article and
`.gitignore` excludes it. This must print nothing:

```bash
git ls-files paper/
```

## 3. Deploy on Streamlit Community Cloud

1. Go to https://share.streamlit.io and **Continue with GitHub**
2. Click **Create app** → **Deploy a public app from GitHub**
3. Fill in:
   - Repository: `YOUR-USERNAME/wine-quality-ml-project`
   - Branch: `main`
   - Main file path: `app/streamlit_app.py`
   - App URL: something like `wine-quality-surianandhan`
4. Open **Advanced settings** → Python version **3.11** → Save
5. Click **Deploy**

The first start takes 2–4 minutes (it installs the packages in `app/requirements.txt`, then
trains the two models). After that it loads in a few seconds.

## 4. Send back the two links

- the app: `https://<your-app-url>.streamlit.app`
- the code: `https://github.com/YOUR-USERNAME/wine-quality-ml-project`

They go into the report (web-application chapter and source-code chapter) and the
paper's Data Availability statement: set `APP_URL` and `REPO_URL` in
`report/tools/results.py` and rebuild (HOW_TO_RUN.md §6b).

## If something goes wrong

| Symptom | Fix |
|---|---|
| `git: command not found` | Run `xcode-select --install`, then retry |
| GitHub asks for a password on push | Use a personal access token: GitHub → Settings → Developer settings → Tokens |
| Streamlit Cloud: "ModuleNotFoundError" | Check the main file path is exactly `app/streamlit_app.py` |
| App shows a red error after an update | In the Streamlit Cloud menu choose **Reboot app** (clears the cached models) |
