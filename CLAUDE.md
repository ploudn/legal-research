# legal_research — Shared Instructions

Instructions for all research projects in this workspace. Each project subfolder has its own `CLAUDE.md` for project-specific details; this file governs shared tools, workflow, and standards that apply everywhere.

---

## Workspace layout

```
legal_research/
  CLAUDE.md               ← this file (shared instructions)
  tools/
    convert.py            ← PDF/EPUB → txt converter (use for every project)
  agents/
    README.md             ← how to use the peer-review framework
    paper_intake_template.md
    agent1_doctrinal.md
    agent2_methods.md
    agent3_generalist.md
    editor_synthesis.md
    runner.py             ← API-based automation
  puiut/                  ← AI governance paper
  French_corp_gov/        ← French corporate governance empirical paper
  [other projects]/
```

---

## Standard research workflow

Every paper follows the same sequence. Steps 1–3 happen before I am involved; the rest is collaborative.

**1. You gather sources.** Download papers (PDF, EPUB), take notes in Word or markdown, draft an outline.

**2. You hand me the sources.** Drop PDFs/EPUBs into the project's `Papers/` folder (or equivalent). Tell me new files have been added.

**3. I convert sources to txt.** I run `tools/convert.py` to produce txt versions with printed page numbers embedded as `=== [Page X] ===` markers. These are what I read — never the raw PDFs. OCR is applied automatically when text extraction fails (image-only scans, DRM-watermarked files).

**4. I do a literature review.** I read the relevant txt files and produce a structured review ordered by relevance to the specific argument being developed. Each entry has: summary, key quotes with page numbers, relevance rating.

**5. I write a section.** Before writing, I read: (a) the overall paper outline, (b) any rider/notes file you've provided, (c) the relevant txt papers. I propose a plan before writing. Output is always `.md` + `.docx`.

**6. You revise and return the draft.** You give me the revised text (or specific passages). I integrate your changes.

**7. I run the peer-review framework.** When a section or the full paper is ready for challenge, I run the three-agent review system (see `agents/README.md`). We agree on the intake template settings before I run it.

---

## Source conversion

**Always read from txt, never from PDFs directly.** Cite the printed page number shown in `=== [Page X] ===` markers (`~X` means approximate).

To convert all new PDFs/EPUBs in a project:
```bash
python3 /Users/main/Documents/workspace/legal_research/tools/convert.py --root Papers/
```

To check for missing conversions only (no conversion):
```bash
python3 /Users/main/Documents/workspace/legal_research/tools/convert.py --root Papers/ --check
```

To force re-conversion of a specific file (e.g. after replacing a bad scan):
```bash
python3 /Users/main/Documents/workspace/legal_research/tools/convert.py --root Papers/ --force filename.pdf
```

The converter handles:
- **PDF** — text extraction via PyMuPDF; automatic OCR fallback (Tesseract) for image-only pages
- **EPUB** — text extraction with chapter markers

Output mirrors the source directory structure under `Papers/txt/`.

---

## Writing sections

Each section is a `.md` file:
- ~2000 words of body text (footnotes excluded)
- `**bold**`, `*italic*`, `[^n]` for footnote refs
- Footnote definitions at bottom: `[^n]: full citation text`
- Citation style: Oxford OSCOLA-adjacent (Author, 'Title' (Year) Volume Journal Page, pinpoint)
- Formatting reference lives in each project folder (usually a `.docx` reference chapter)

Before writing any section, literature review, or summary, I will:
1. Read the outline and any rider/notes file
2. Propose a short plan: scope, structure, key sources, intended conclusion
3. Ask explicitly for the intended conclusion if it is not clear from the outline or notes
4. Wait for approval before writing

This applies to every piece of writing, not just full sections. The intended conclusion — what the reader should believe after reading — is the single field most likely to cause wasted iterations if missing.

---

## Docx conversion

Each project has a `make_[section]_docx.py` conversion script. When writing a new section for a project that doesn't yet have one, I will create it based on the project's formatting reference. Formatting parameters are stored in each project's CLAUDE.md.

---

## Peer-review framework

Three specialised agents + an editorial synthesis. See `agents/README.md` for full instructions.

**Before running:** fill in `agents/paper_intake_template.md` and show it to me. I will suggest any tweaks needed for the specific paper (field, methodology type, target journal) and wait for your approval before running.

**Modes:**
- **Review** — challenge an existing draft; produces a prioritised action list
- **Create** — draft from notes; agents run sequentially, each building on the previous

The agent personas are calibrated for legal and law-adjacent scholarship. For papers with a strong empirical component, Agent 2 (methods) and the intake template may need adjustment — I will flag this.

---

## Challenges to this workflow — and proposed improvements

These are tensions in the current approach worth discussing:

**1. Notes in Word (.docx) are fine.** When you provide a `.docx` notes or rider file, I will convert it to txt automatically before reading. No action needed on your end.

**2. The peer-review agents are calibrated for corporate law / governance.** For papers in administrative law, AI regulation, or other fields, Agent 1's expertise list and Agent 3's lenses need field-specific tweaks. I will propose these each time before running.

**3. Literature reviews have no standard template.** Currently they are ad hoc. A consistent format (summary / key quotes / relevance / fit-with-argument) makes them easier to convert into footnotes later. The reviews produced so far follow this format; I will keep it.

**4. No cross-project paper tracking.** A paper downloaded for one project might be relevant to another. There is currently no way to know this. If this becomes a problem, I can maintain a `legal_research/master_bibliography.md` listing all papers across projects.

**5. Section drafts have no version history beyond git.** If you revise a section heavily and then want to go back, git is the only record. Consider committing before sending me a revised draft to review.

---

## Git and GitHub

Each project has its own GitHub repo (e.g. `ploudn/puiut`, `ploudn/French_corp_gov`). The `legal_research` folder itself has its own repo (`ploudn/legal-research`) for shared tools and instructions only — project subfolders are not part of it (they are separate repos, not submodules).

Files that should never be committed (add to each project's `.gitignore`):
```
Papers/*.pdf
Papers/**/*.pdf
Papers/**/*.epub
Papers/txt/
*.docx
~$*
.DS_Store
```
