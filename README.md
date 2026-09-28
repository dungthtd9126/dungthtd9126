<div align="center">
  <img src="assets/home-neon-cat.webp" alt="A silhouetted cat watching a violet city glow through a window." width="760" />
  <h1>Saitomu</h1>
  <p><strong>Pwner / Binary Exploitation</strong><br />CTF · PWN · REVERSE · KERNEL</p>
  <p>I explore binary exploitation, reverse engineering, and Linux kernel security—and document what I learn along the way.</p>
  <p>
    <a href="https://github.com/dungthtd9126">GitHub</a> ·
    <a href="https://hackmd.io/IEqCkk2GRHe3qK5KhcyuGQ">HackMD notes</a> ·
    <a href="https://pwnable.tw/user/40468">pwnable.tw</a> ·
    <a href="https://github.com/dungthtd9126/vercel-portfolio">Portfolio source</a>
  </p>
</div>

---

## About

I'm a CTF player interested in the details beneath the surface: memory layouts, calling conventions, allocators, and loaders. I work from reproducing a behavior and tracing its cause to building a proof of concept, then write up the process so the reasoning is useful later.

> Small steps. Deeper understanding.

## Focus

- **Binary exploitation:** heap primitives, out-of-bounds bugs, format strings, leaks, and ROP.
- **Linux kernel:** internals and exploitation techniques including overflows, use-after-free bugs, and race conditions.
- **Reverse engineering:** understanding how compiled programs behave and where their assumptions break.
- **Learning in public:** CTF write-ups, reusable notes, and references.

## Selected repositories

| Repository | Topics |
| --- | --- |
| [0xlaugh & VSL CTF write-ups](https://github.com/dungthtd9126/0xlaugh-And-VSL-ctf-write-up) | Seccomp, shellcode, format strings, leaks, and ROP |
| [write-up-task-CLB](https://github.com/dungthtd9126/write-up-task-CLB) | Binary exploitation notes, FSOP, FILE structures, and ret2dlresolve |
| [WU_loc_tv](https://github.com/dungthtd9126/WU_loc_tv) | OOB bugs, heap manipulation, arbitrary read/write, races, and ROP |
| [LK_pwnyable_learning](https://github.com/dungthtd9126/LK_pwnyable_learning) | Linux kernel exploitation write-ups |
| [CTF-note](https://github.com/dungthtd9126/CTF-note) | CTF notes, references, and reusable techniques |

## Write-ups & notes

- [KCSC Recruitment 2025 — PWN](https://hackmd.io/IEqCkk2GRHe3qK5KhcyuGQ)
- [KMA CTF 2026](https://hackmd.io/@gbCdQ_ljS7ujEO84BSXzYw/SJAGejUgGl)
- [Lac CTF FSOP notes](https://github.com/dungthtd9126/Lac-CTF)

## How I work

**Reproduce** the behavior · **Understand** the mechanism · **Build** a proof of concept · **Document** the path, including what did not work.

## Portfolio website

This repository also contains my dependency-free portfolio site. Its pages are:

- `index.html`: Home and selected repositories
- `about.html`: About
- `writeups.html`: Notes & Learning, split into write-ups and notes
- `writeup.html?id=<slug>`: Native Markdown reader
- `resources.html`: Practice links, references, and documentation
- `contact.html`: Contact and external profiles

Old hash bookmarks still work. `skills.html` and `#/skills` redirect to Resources. The **SKILLS filter inside Notes & Learning remains named SKILLS**.

## Future content updates

Send a link and its category or resource group. The repository's `../AGENTS.md` records the workflow for future coding sessions.

**Edit `content.json`; do not edit generated `data.js` or section HTML files.** The add commands update the JSON, validate it, and regenerate all browser files automatically. They need Python 3.10 or newer and no extra packages.

## Section images

Section imagery is configured in `content.json` under `sectionImages` and stored locally in `assets/`. Images are kept local so the site does not depend on remote hotlinks:

- `assets/home-neon-cat.webp`: user-provided image
- `assets/resources-library.webp`: `https://www.pinterest.com/pin/10766486606045215/`
- `assets/writeups-study-cat.png`: user-provided image
- `assets/contact-cat-phone.webp`: user-provided image

Run these commands from this directory.

### Add an external write-up

```bash
python3 manage_content.py add-writeup \
  --url "https://github.com/owner/repo" \
  --title "Example write-up" \
  --category PWN \
  --summary "A short, accurate description of the write-up." \
  --tags heap ROP
```

Categories: **PWN, KERNEL, MOBILE, SKILLS**. `ALL` is generated automatically. Tags are separate from categories.

Use `--collection notes` for entries that belong in the Notes subsection; omit it for challenge write-ups. Existing IDs and destinations can be moved between collections with `--update --id`.

The command generates a stable ID from the title. Use `--id my-note` to choose one. Optional flags: `--date YYYY-MM-DD` and `--source "Source name"`. Unknown publication dates should be omitted. Source labels are inferred for GitHub, HackMD, and local Markdown.

### Add a resource

```bash
python3 manage_content.py add-resource \
  --url "https://example.com/guide" \
  --title "Example guide" \
  --group "Systems references" \
  --summary "A short explanation of when this reference is useful."
```

Existing group names are matched without regard to case. A new group is created when needed. This adds a link to the **Resources page**, independently of the Notes & Learning categories.

### Update an existing entry

Repeat the relevant add command with `--update`. Matching write-up URLs, local files, or explicit IDs identify existing entries; resources are matched by URL. Without `--update`, duplicates produce an error and leave the files unchanged.

- Write-up IDs stay unchanged even when the title changes.
- To change a write-up's destination, supply its existing `--id` and the new `--url` or `--file`.
- Omitted tags and dates are retained during write-up updates.
- To move a resource, use its URL with `--update --group "New group"`.
- Add `--dry-run` to either command to validate and display the entry without writing files.

The existing `write-up-task-CLB` entry has ID `club-pwn-notes` and belongs in **PWN**. `LK_pwnyable_learning` belongs in **KERNEL**.

### Host a Markdown write-up

Create `content/my-note.md`, using `content/_template.md` as a starting point. Then register it:

```bash
python3 manage_content.py add-writeup \
  --file content/my-note.md \
  --id my-note \
  --title "My note" \
  --category PWN \
  --collection notes \
  --summary "What this note covers."
```

The file must already exist inside `content/`. The card opens `writeup.html?id=my-note`; no extra HTML file is needed.

Markdown supports headings, paragraphs, bullet lists, blockquotes, fenced code, inline code, bold/italic text, and HTTP(S) links.

## Manual edits and validation

All content remains editable as ordinary JSON:

| Field in `content.json` | Controls |
| --- | --- |
| `categories` | Notes & Learning filters |
| `writeups`, `notes` | Entries shown in Notes & Learning |
| `resourceGroups` | Resource groups and links |
| `repositories` | Featured repositories on Home |
| `links` | Main external profiles |
| `sectionImages` | Local image, alt text, and caption for each page |
| `profile`, `currentFocus`, `workflow` | Profile, About, and Resources content |

After editing JSON, CSS, JavaScript, or the shared page template manually:

```bash
python3 sync_data.py
python3 sync_data.py --check
```

Validation checks required fields, known categories, duplicate IDs and destinations, dates, URL formats, and local Markdown paths. All outputs are prepared before writing; invalid content leaves generated files untouched. URL validation checks format, not remote availability.

The generator updates `data.js` and each HTML page's embedded content, CSS, and JavaScript. A single-file preview can display that page with its embedded fallback. Navigation needs the complete folder; Markdown loading needs an HTTP preview.

## Local preview

```bash
python3 -m http.server 8000
```

Open `http://localhost:8000/`.

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

When changing the content tools:

```bash
python3 -B -m unittest discover -s tests -v
```

Tests use temporary copies and do not add sample entries to the live portfolio.

## GitHub Pages

Deploy the generated HTML pages, `data.js`, `content/`, and `assets/` together. Relative links work at a custom domain or a project URL such as `https://username.github.io/portfolio/`. No npm dependencies, server rewrites, or custom 404 routing are required.

Keep `content.json`, the generator, and the other source files in the repository so future updates remain reproducible.
