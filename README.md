# How this works — a guide for myself

This document explains the architecture of my research setup and what I need to do each time I start a new paper. Written to be understood without programming knowledge.

---

## 1. The big picture

I write multiple academic papers. Each paper is its own project. Rather than rebuilding tools from scratch for every project, I have a shared folder — `legal_research/` — that contains tools and instructions used by all projects.

Here is how it looks on my computer:

```
Documents/
  workspace/
    legal_research/          ← shared tools and instructions (this folder)
      README.md              ← this file
      CLAUDE.md              ← instructions for Claude (applies to all projects)
      tools/
        convert.py           ← script that converts PDFs and EPUBs to readable text
      agents/                ← peer-review framework (see section 4 below)
    puiut/                   ← my AI governance paper
    French_corp_gov/         ← my French corporate governance paper
    finreg/                  ← (future paper)
    ...
```

`legal_research/` sits **alongside** the paper folders — they are all siblings inside `workspace/`. `legal_research/` does not contain the paper folders; it is simply a dedicated place for shared tools that any paper project can use.

---

## 2. What GitHub is and how it fits in

**What GitHub is.** GitHub is a website that stores copies of my files online, keeps track of every version I save, and lets me see what changed between versions. Think of it like a very powerful version of Word's "Track Changes," but for entire folders of files.

**Repository (repo).** A "repository" is just a folder that GitHub is tracking. Every time I save a meaningful change, I create a "commit" — a snapshot of the folder at that moment. GitHub keeps all the snapshots.

**How my repos are organised.** I have one repo per project, plus one for the shared tools:

| Folder on my computer | GitHub repo | What it contains |
|---|---|---|
| `legal_research/` | `ploudn/legal-research` | Shared tools and instructions only |
| `puiut/` | `ploudn/puiut` | AI governance paper |
| `French_corp_gov/` | `ploudn/French_corp_gov` | French corporate governance paper |

Each paper folder is tracked independently. The `legal_research/` folder does **not** contain or track the paper folders — it only contains the shared tools. This means I can update a shared tool once and all papers benefit, without mixing up the histories of different projects.

**What is not on GitHub.** PDFs, Word documents, and converted text files are excluded from GitHub on purpose. They are large, often private, and not the kind of thing that needs version history. Only code, instructions, and written outputs (`.md` files) are tracked.

---

## 3. How Claude knows what to do

Claude reads a file called `CLAUDE.md` at the start of every session. This file contains instructions.

There are two layers:

- **Shared instructions** — `legal_research/CLAUDE.md` — apply to all papers (how to convert PDFs, how to write sections, how to run the peer-review framework, etc.). Claude reads this because every paper folder references it explicitly.
- **Project-specific instructions** — e.g. `puiut/CLAUDE.md` — apply only to that paper (where the outline is, what citation style to use, which sources are most important, etc.).

So when I work on `puiut`, Claude reads both files: the shared one first, then the project-specific one. The project-specific one can override or add to anything in the shared one.

---

## 4. The tools

### `tools/convert.py` — converting PDFs to readable text

Claude cannot read PDFs directly. This script converts PDFs (and EPUBs) into plain text files that Claude can read. It embeds page number markers (`=== [Page X] ===`) so that when Claude quotes something, it can give me the exact page number from the original document.

I never need to run this script myself — I just tell Claude that I have added new PDFs, and Claude runs it.

The converted text files are saved in a `txt/` subfolder inside whichever `Papers/` folder I point it at. They mirror the structure of the original folder.

### `agents/` — the peer-review framework

This is a set of three AI reviewers plus an editor that synthesises their comments:

- **Agent 1** reviews the legal argument, theory, and literature
- **Agent 2** reviews the methodology (less relevant for purely doctrinal papers)
- **Agent 3** looks at the paper from adjacent disciplines — economics, political science, policy

The three reviews are then merged into a single editorial letter with prioritised action items.

I use this when a section or full paper is ready to be challenged. I do not run it myself — I ask Claude to run it and we agree on the settings first.

---

## 5. Starting a new paper — checklist

When I begin a new paper, here is what needs to happen, in order:

### What I do myself

1. **Create a folder** inside `legal_research/` with a short name (e.g. `insider_trading/`).
2. **Create a `Papers/` subfolder** inside it and put my PDFs there. I can organise PDFs into subfolders by topic if I want — the conversion tool will handle any structure.
3. **Download or draft an outline** — either a Word document or a simple text file describing the paper's structure and argument.
4. **(Optional) Write a rider/notes file** for each section I want Claude to work on — this is just a Word or text file with my thoughts, quotes I want included, arguments I want made, etc.

### What I ask Claude to do

1. **"Set up the project"** — Claude will:
   - Create a `CLAUDE.md` in the new folder with project-specific instructions (citation style, formatting reference, key sources, etc.)
   - Add the reference to the shared `legal_research/CLAUDE.md` at the top
   - Create a `.gitignore` so PDFs and Word docs are excluded from GitHub
   - Initialise a GitHub repo for the project

2. **"Convert the PDFs"** — Claude runs `convert.py` on my `Papers/` folder. If any PDFs are image-only scans, OCR kicks in automatically.

3. **"Do a literature review on [topic/argument]"** — Before Claude starts, it will propose a plan (which papers to include, how to order them, what angle to take) and ask me to confirm. Then it reads the relevant text files and produces the review.

4. **"Write [section name]"** — Before Claude starts, it will propose a plan and ask for the intended conclusion of the section if I have not already given it. Once I confirm, it writes the section as a `.md` file and converts it to a formatted Word document.

5. **"Run the peer-review framework on [section/paper]"** — Claude will ask me to fill in a short intake form first (what is the paper about, what journal is it for, etc.), suggest any tweaks, and then run the three agents.

---

## 6. Things to keep in mind

**PDFs are not tracked by GitHub.** If I get a new computer or lose my local files, the PDFs will not be recoverable from GitHub. Back them up separately (e.g. on an external drive or cloud storage).

**Commit regularly.** After Claude produces a section or a significant piece of writing, it is worth committing to GitHub. This creates a checkpoint I can return to. I can ask Claude to do this: "commit what we've done so far."

**Each paper is self-contained.** Literature reviews, bibliographies, and converted text files all live inside the paper's own folder. Nothing is shared between papers. If the same paper appears in two projects, it will be converted separately in each one.

**The `legal_research/` repo only tracks tools.** If I update a tool (e.g. the conversion script or an agent prompt), that change goes into `ploudn/legal-research` on GitHub. It does not affect the paper repos.
