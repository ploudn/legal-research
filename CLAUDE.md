# legal_research — Shared Instructions

Shared tools and conventions for all research projects in this workspace. Each project has its own `CLAUDE.md` for project-specific details.

---

## Workspace layout

```
workspace/
  legal_research/         ← this folder (shared tools only)
    CLAUDE.md
    tools/
      convert.py          ← PDF/EPUB → txt converter
    agents/
      README.md
      paper_intake_template.md
      agent1_doctrinal.md
      agent2_methods.md
      agent3_generalist.md
      editor_synthesis.md
      runner.py
  puiut/                  ← AI governance paper (sibling, not subfolder)
  French_corp_gov/        ← French corporate governance paper
  [other projects]/
```

---

## Typical workflow

Papers usually proceed in this order, though not always linearly:

- Sources gathered and dropped into the project's `Papers/` folder
- Sources converted to txt (see below)
- Literature review produced for the relevant argument
- Sections drafted and revised iteratively
- Peer-review framework run when a draft is ready for challenge

---

## Source conversion

**Always read from txt, never from PDFs directly.** Cite the printed page number shown in `=== [Page X] ===` markers (`~X` means approximate).

When told new files have been added, run:
```bash
python3 /Users/main/Documents/workspace/legal_research/tools/convert.py --root Papers/
```

Other options:
```bash
--check          # list missing conversions only, no conversion
--force FILE     # re-convert a specific file
--file RELPATH   # convert a single file
```

The converter handles PDF (text extraction + automatic OCR fallback for image-only pages) and EPUB (chapter markers). Output mirrors the source structure under `Papers/txt/`.

---

## Before writing anything

Before writing any section, literature review, or summary:
1. Read the outline and any rider/notes file (convert `.docx` files to txt first if needed)
2. Propose a plan: scope, structure, key sources, intended conclusion
3. If the intended conclusion is not explicit, ask for it before proceeding
4. Wait for approval

The intended conclusion — what the reader should believe after reading — is the most important input. The same sources can support different arguments depending on framing; writing without it causes wasted iterations.

---

## Writing sections

Each section is a `.md` file:
- ~2000 words of body text (footnotes excluded)
- `**bold**`, `*italic*`, `[^n]` for footnote refs; footnote definitions at bottom
- Citation style: Oxford OSCOLA-adjacent — Author, 'Title' (Year) Volume Journal Page, pinpoint
- Formatting reference and docx conversion script live in each project folder

---

## Literature reviews

Format: per paper — summary (3–6 sentences), key quotes with printed page numbers, relevance rating. Papers ordered by decreasing relevance to the specific argument. Bibliographies and literature reviews are per paper, not shared across projects.

---

## Peer-review framework

Three agents + editorial synthesis. See `agents/README.md` for full instructions.

Before running: show me the filled-in `agents/paper_intake_template.md`. I will propose any field-specific tweaks and wait for approval before running.

---

## Git and GitHub

Each project has its own repo (`ploudn/puiut`, `ploudn/French_corp_gov`, etc.). The `legal_research` repo (`ploudn/legal-research`) holds shared tools only — project subfolders are separate repos, not submodules.

Standard `.gitignore` entries for each project:
```
Papers/**/*.pdf
Papers/**/*.epub
Papers/txt/
*.docx
~$*
.DS_Store
```
