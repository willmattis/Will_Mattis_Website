# Will Mattis — Portfolio

A fast, static portfolio site. No frameworks, no build step — just HTML, CSS, and
a little JavaScript. **All of your content lives in one file: [`js/data.js`](js/data.js).**

---

## How to view it locally

The site now includes an **in-browser 3D STEP viewer**, which uses JavaScript
modules — those only work over `http://`, not by double-clicking the file. So run
the included tiny server from the **project root** (the folder above `site/`):

```
python serve.py
```

then open <http://localhost:8123>. (Press Ctrl+C to stop it.)

> Why not `python -m http.server`? On Windows it serves `.js` files with the wrong
> type, which breaks the 3D viewer. `serve.py` fixes that. The live GitHub Pages
> site doesn't need any of this — GitHub serves the correct types automatically.

---

## How to add or edit a project (the part you'll use most)

1. Open **`js/data.js`** in any text editor (VS Code, Notepad, etc.).
2. Find the `projects: [ ... ]` list.
3. **Copy one whole `{ ... }` block** (from `{` to the `},`), paste it as a new
   entry, and change the fields. The only required fields are `slug`, `title`,
   `thumb`, and `summary`.
4. Save. Refresh the page. Done — the card and its detail page appear automatically.

### A minimal new project looks like this:

```js
{
  slug: "my-new-board",                 // unique, lowercase-with-dashes
  title: "My New Board",
  subtitle: "One-line description",
  org: "Bearcats Electric Racing",
  date: "2026",
  status: "Prototype",                  // small badge; remove line to hide
  tags: ["Altium", "STM32"],
  thumb: "assets/img/card-my-new-board.svg",   // see "Images" below
  summary: "A sentence or two shown on the card and at the top of the page.",
  role: "What you personally did on this project.",
  highlights: [
    "First headline achievement",
    "Second headline achievement"
  ],
  sections: [
    { heading: "Overview", body: "A paragraph..." },
    { heading: "How it works", body: "Another paragraph..." }
  ],
  specs: [
    { label: "MCU", value: "STM32G4" },
    { label: "Tool", value: "Altium Designer" }
  ],
  gallery: [
    { src: "assets/img/my-photo.jpg", caption: "Caption under the image" }
  ],
  files: [
    { label: "Schematic (PDF)", href: "assets/files/my-schematic.pdf", kind: "pdf" },
    { label: "3D model (STEP)", href: "assets/files/my-board.step", kind: "step" }
  ],
  links: [
    { label: "GitHub repo", href: "https://github.com/..." }
  ]
}
```

Every list field (`tags`, `highlights`, `sections`, `specs`, `gallery`, `files`,
`links`) is optional — delete any you don't need.

### Sections (groups)
Projects are grouped on the homepage by their **`group`** field (e.g.
`"Bearcats Electric Racing"`, `"X-Inator"`, `"School Projects"`). The order of the
sections — and the one-line blurb under each — is controlled by the `groups` array
near the top of `js/data.js`. To add a new section, add an entry there and set
matching `group:` values on the projects that belong to it.

### Interactive 3D model (STEP viewer)
To show a spinnable 3D model on a project page, add a **`model:`** field pointing at
a `.step` / `.stp` file in `assets/files/`:

```js
model: "assets/files/my-board.step",
```

The project page then shows a **"Load interactive 3D model"** button. The model is
parsed and rendered right in the browser (drag to rotate, scroll to zoom) — no
conversion needed, just drop the `.step` file in and reference it. Large files take
a few seconds to load; there's always a "download the STEP file" fallback too.

### Editing your bio / name / links
Edit the `profile` object at the top of `js/data.js` (name, tagline, about text,
email, LinkedIn, GitHub, résumé, and the skills list).

> **Add your LinkedIn / GitHub:** in `profile.links`, fill in the empty `""`
> strings. Empty ones are hidden automatically.

---

## Images

- **Card thumbnails** live in `assets/img/`. The four starter boards use generated
  SVG thumbnails (`card-*.svg`). To use a real photo or 3D render instead, drop a
  `.jpg`/`.png` in `assets/img/` and point the project's `thumb` at it.
- **Gallery images & schematics** also live in `assets/img/`. The schematic PNGs
  were generated from your PDFs.
- **Downloadable files** (PDF, STEP, etc.) live in `assets/files/`.

To add a board photo later: take a photo, save it to `assets/img/`, and either set
it as the project's `thumb` or add it to that project's `gallery`.

---

## Publishing it (making it public)

### Option A — GitHub Pages (recommended, free, auto-deploys)
This repo already includes a workflow at `.github/workflows/deploy.yml` that
publishes the `site/` folder automatically. One-time setup:

1. Create a repo on GitHub and push this project to it (see the root `DEPLOY.md`
   for the exact commands).
2. On GitHub: **Settings → Pages → Build and deployment → Source: GitHub Actions**.
3. Every `git push` to `main` now rebuilds and deploys the site. Your URL will be
   `https://<your-username>.github.io/<repo-name>/`.

> The whole site is relative-path safe, so it works whether it's served at a domain
> root or under a `/<repo-name>/` subpath like GitHub Pages uses.

### Option B — Netlify (free, drag-and-drop)
1. Go to <https://app.netlify.com/drop> and drag the **`site`** folder on.
2. Live in seconds at a `something.netlify.app` URL. A `netlify.toml` is included.

### Custom domain
On GitHub Pages: **Settings → Pages → Custom domain** (e.g. `willmattis.com`) and
follow the DNS instructions. A domain is ~$10–15/yr.

### Custom domain
On Netlify/Vercel: project → **Domain settings** → add your domain (e.g.
`willmattis.com`) and follow the DNS instructions. A domain is ~$10–15/yr.

---

## File map

```
site/
├── index.html          Homepage (hero, projects, about, contact)
├── project.html        Project detail page (one template for all projects)
├── netlify.toml        Netlify config (no build needed)
├── css/styles.css      All styling — change --accent to re-theme
├── js/
│   ├── data.js         ← YOUR CONTENT. Edit this.
│   ├── main.js         Renders the homepage
│   └── project.js      Renders project detail pages
└── assets/
    ├── img/            Thumbnails, schematics, photos, favicon
    └── files/          Downloadable PDFs, STEP models, etc.
```
