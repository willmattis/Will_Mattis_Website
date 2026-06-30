# Putting this portfolio online (GitHub Pages)

This repo is already a git repository with an initial commit and a deploy workflow.
You just need to create a GitHub repo, push to it, and turn Pages on. ~5 minutes,
one time. After that, every `git push` updates the live site automatically.

---

## 1. Create an empty repo on GitHub
Go to <https://github.com/new> and:
- **Repository name:** `portfolio` (or whatever you like)
- **Visibility:** Public
- **Do NOT** check "Add a README / .gitignore / license" — keep it empty.
- Click **Create repository**.

## 2. Push this project to it
Open a terminal **in this folder** and run (replace `YOUR-USERNAME` and the repo
name if you changed it):

```bash
git remote add origin https://github.com/YOUR-USERNAME/portfolio.git
git branch -M main
git push -u origin main
```

If git asks you to sign in, use your GitHub username and a **Personal Access Token**
as the password (create one at <https://github.com/settings/tokens> → "Generate new
token (classic)" → check the `repo` box). Or install GitHub Desktop and push from there.

## 3. Turn on GitHub Pages
On your repo page: **Settings → Pages → Build and deployment** →
set **Source = GitHub Actions**. That's it.

The included workflow (`.github/workflows/deploy.yml`) runs automatically on every
push, publishes the `site/` folder, and gives you a live URL:

```
https://YOUR-USERNAME.github.io/portfolio/
```

(Check the **Actions** tab to watch the first deploy; it takes ~1 minute.)

---

## Updating the site later
1. Edit `site/js/data.js` (add a project, change your bio, etc.).
2. Save, then:
   ```bash
   git add -A
   git commit -m "Add new project"
   git push
   ```
3. ~1 minute later the live site updates itself.

## Preview locally before pushing
From this folder: `python serve.py`, then open <http://localhost:8123>.

---

## Notes
- The big original CAD source folders (`BMS_Main/`, `Motor/`, `X-Inator/`, …) are
  **not** pushed — they're in `.gitignore`. The files the website actually needs are
  already copied into `site/assets/`, so the repo stays small. If you ever want to
  back up the originals in the repo too, remove their lines from `.gitignore`.
- A custom domain (e.g. `willmattis.com`) can be added later under Settings → Pages.
