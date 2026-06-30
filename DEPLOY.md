# Putting this portfolio online (GitHub Pages)

This folder is already a git repository with commits and a deploy workflow. You just
need to publish it to GitHub and turn Pages on — about 5 minutes, one time. After
that, every change you commit + push updates the live site automatically.

Your live URL will be: **https://willmattis.github.io/portfolio/**

---

## Option 1 — GitHub Desktop (what you're using)

1. **File → Add Local Repository** → choose this folder
   (`C:\Users\Will Mattis\Documents\GitHub\portfolio`) → **Add**.
   (It already has git history, so Desktop just picks it up.)
2. Click **Publish repository** in the top bar.
   - **Name:** `portfolio`
   - **Uncheck "Keep this code private"** (Pages needs it public on a free account).
   - **Publish repository**.
3. Open the repo on github.com → **Settings → Pages → Build and deployment** →
   set **Source = GitHub Actions**.
4. Go to the **Actions** tab. If the first run errored because Pages wasn't on yet,
   click it → **Re-run jobs**. When it's green, your site is live at the URL above.

**To update later:** edit `site/js/data.js`, then in GitHub Desktop write a summary,
**Commit to main**, and **Push origin**. ~1 minute later the live site updates.

---

## Option 2 — Command line (if you ever prefer it)

```bash
git remote add origin https://github.com/willmattis/portfolio.git
git branch -M main
git push -u origin main
```

Then do steps 3–4 above. (Git may ask you to sign in with a Personal Access Token
from <https://github.com/settings/tokens> — check the `repo` box.)

---

## Preview locally before pushing
From this folder: `python serve.py`, then open <http://localhost:8123>.

## Notes
- The big original CAD source folders (`BMS_Main/`, `Motor/`, `X-Inator/`, …) are in
  `.gitignore` and won't be pushed — the files the site needs are already in
  `site/assets/`. Remove a line from `.gitignore` if you ever want to track one.
- Custom domain (e.g. `willmattis.com`) can be added later under Settings → Pages.
