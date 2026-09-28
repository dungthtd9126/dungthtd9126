# Portfolio setup and maintenance notes

Keep these notes for future portfolio configuration and content-update sessions. The GitHub-facing `README.md` is focused on my profile, blogs, and write-ups.

## Vibe Portfolio One continuity

- **Live portfolio:** https://saitomu.lykn.ru/
- **Design reference:** https://github.com/leonxlnx/taste-skill
- For future visual work on this existing site, use Taste Skill's `redesign-existing-projects` skill. Install it with:

  ```bash
  npx skills add https://github.com/Leonxlnx/taste-skill --skill "redesign-existing-projects"
  ```

## Site pages

The site is dependency-free and uses separate HTML pages:

- `index.html`: Home and selected repositories
- `about.html`: About
- `writeups.html`: Notes & Learning, split into write-ups and notes
- `writeup.html?id=<slug>`: Native Markdown reader
- `resources.html`: Practice links, references, and documentation
- `contact.html`: Contact and external profiles

Old hash bookmarks still work. `skills.html` and `#/skills` redirect to Resources. The **SKILLS filter inside Notes & Learning remains named SKILLS**.

## Content source and generated files

Edit `content.json`; do not edit generated `data.js` or section HTML files. The add commands update the JSON, validate it, and regenerate the browser files. They require Python 3.10 or newer and no extra packages.

Content fields in `content.json`:

| Field | Controls |
| --- | --- |
| `categories` | Notes & Learning filters |
| `writeups`, `notes` | Entries shown in Notes & Learning |
| `resourceGroups` | Resource groups and links |
| `repositories` | Featured repositories on Home |
| `links` | Main external profiles |
| `sectionImages` | Local image, alt text, and caption for each page |
| `profile`, `currentFocus`, `workflow` | Profile, About, and Resources content |

## Section images

Section imagery is configured in `content.json` under `sectionImages` and stored locally in `assets/`:

- `assets/home-neon-cat.webp`: user-provided image
- `assets/resources-library.webp`: `https://www.pinterest.com/pin/10766486606045215/`
- `assets/writeups-study-cat.png`: user-provided image
- `assets/contact-cat-phone.webp`: user-provided image

The GitHub-facing README uses a separate, short crop at `assets/github-profile-cat.webp`; the original `home-neon-cat.webp` remains unchanged for the site.

## Add or update an external write-up

Run from the portfolio directory:

```bash
python3 manage_content.py add-writeup \
  --url "https://github.com/owner/repo" \
  --title "Example write-up" \
  --category PWN \
  --summary "A short, accurate description of the write-up." \
  --tags heap ROP
```

Categories: **PWN, KERNEL, MOBILE, SKILLS**. `ALL` is generated automatically. Tags are separate from categories. Use `--collection notes` for entries in the Notes subsection; omit it for challenge write-ups. The command generates a stable ID from the title; use `--id my-note` to choose one. Optional flags include `--date YYYY-MM-DD` and `--source "Source name"`. Unknown publication dates should be omitted.

Repeat the command with `--update` to edit an existing entry. Matching URLs, local files, or explicit IDs identify existing write-ups. IDs stay unchanged when titles change; use the existing `--id` with a new `--url` or `--file` to change the destination. Omitted tags and dates are retained. Use `--dry-run` to validate and preview without writing files.

The existing `write-up-task-CLB` entry has ID `club-pwn-notes` and belongs in **PWN**. `LK_pwnyable_learning` belongs in **KERNEL**.

## Add or update a resource

```bash
python3 manage_content.py add-resource \
  --url "https://example.com/guide" \
  --title "Example guide" \
  --group "Systems references" \
  --summary "A short explanation of when this reference is useful."
```

Resources are matched by URL. Use `--update --group "New group"` to move one. Group names are matched without regard to case; a new group is created when there is no match. Resources appear on the Resources page, independently of Notes & Learning categories.

## Host a Markdown write-up

Create a Markdown file inside `content/`, using `content/_template.md` as a starting point, then register it:

```bash
python3 manage_content.py add-writeup \
  --file content/my-note.md \
  --id my-note \
  --title "My note" \
  --category PWN \
  --collection notes \
  --summary "What this note covers."
```

The file must already exist inside `content/`. Its card opens `writeup.html?id=my-note`; no extra HTML file is needed. Markdown supports headings, paragraphs, lists, blockquotes, fenced and inline code, bold/italic text, and HTTP(S) links.

## Manual edits and validation

After manually editing JSON, CSS, JavaScript, or the shared page template, regenerate and check the site:

```bash
python3 sync_data.py
python3 sync_data.py --check
```

Validation checks required fields, categories, duplicate IDs and destinations, dates, URL formats, and local Markdown paths. The generator updates `data.js` and each HTML page's embedded content, CSS, and JavaScript. Navigation needs the complete folder; loading Markdown requires an HTTP preview.

Local preview:

```bash
python3 -m http.server 8000
```

Open `http://localhost:8000/`.

When changing the content tools, run:

```bash
python3 -B -m unittest discover -s tests -v
```

Tests use temporary copies and do not add sample entries to the live portfolio.

## Project files

```text
content.json          Editable content source
manage_content.py     Add/update commands; rebuild automatically
sync_data.py          Content validation and page generation
page-template.html    Shared document, navigation, and footer
app.js                Page rendering, filters, Markdown, redirects
styles.css            Shared design
data.js               Generated browser data
*.html                Generated pages, except page-template.html
content/              Hosted Markdown notes
assets/               Images
tests/                Content workflow regression tests
```

## GitHub Pages

Deploy the generated HTML pages, `data.js`, `content/`, and `assets/` together. Relative links work at a custom domain or a project URL such as `https://username.github.io/portfolio/`. No npm dependencies, server rewrites, or custom 404 routing are required. Keep `content.json`, the generator, and other source files in the repository so future updates remain reproducible.
