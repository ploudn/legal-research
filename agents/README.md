# Peer Review Agents

Three specialised agents + an editorial synthesis for reviewing or drafting academic legal papers. Field-neutral: works for corporate law, AI governance, administrative law, financial regulation, and adjacent fields.

---

## The agents

| Agent | File | Role |
|---|---|---|
| Agent 1 — Doctrinal & Theoretical | `agent1_doctrinal.md` | Theory, literature, doctrinal accuracy, contribution |
| Agent 2 — Methods | `agent2_methods.md` | Data, methodology, inference, reproducibility |
| Agent 3 — Interdisciplinary | `agent3_generalist.md` | Finance, economics, political science, policy implications |
| Editor Synthesis | `editor_synthesis.md` | Merges the three reviews into one editorial decision |

**Note on field calibration:** Agent 1's expertise list covers corporate law, administrative law, AI governance, and financial regulation. For papers in other subfields, Claude will propose any necessary tweaks to the intake template before running — always approve these first.

---

## Step 0 — Always fill in the intake template first

Open `paper_intake_template.md`, fill in all fields, and show it to Claude. Claude will suggest any field-specific tweaks (e.g. adjusting Agent 2's checklist for a purely doctrinal paper) and wait for your approval before running.

**The most important field is INTENDED CONCLUSION OF THIS SECTION.** Leaving it blank is the single biggest source of wasted iterations.

---

## Option A — Manual use in Claude (no setup needed)

### REVIEW mode

For each agent (run in separate conversations):
1. Open `agent1_doctrinal.md` (or agent2, agent3)
2. Copy everything between `## SYSTEM PROMPT — BEGIN PASTE HERE` and `## SYSTEM PROMPT — END PASTE HERE`
3. Start a new conversation in Claude
4. Paste the system prompt
5. Paste your filled-in intake template
6. Paste the full text of the paper (or section)
7. The agent produces a structured checklist review

After all three: use `editor_synthesis.md` the same way — paste the three reviews and get one consolidated editorial letter.

### CREATE mode (sequential: Agent 1 → 2 → 3)

**Step 1 — Agent 1 (lead author)**
- Paste Agent 1's system prompt + intake template + your research notes
- Agent 1 writes the complete first draft
- Save Agent 1's output

**Step 2 — Agent 2 (methods revision)**
- New conversation; paste Agent 2's system prompt + intake + notes + Agent 1's draft
- Agent 2 improves methodology sections
- Save Agent 2's output

**Step 3 — Agent 3 (final enrichment)**
- New conversation; paste Agent 3's system prompt + intake + notes + Agent 2's draft
- Agent 3 adds interdisciplinary coverage
- This is your final draft

---

## Option B — Automated via the Anthropic API

Runs all agents automatically and saves outputs. Costs ~$0.10–0.50 per full paper review.

### One-time setup

```bash
pip install anthropic
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

### Running a review

```bash
# From any project directory:
python3 /Users/main/Documents/workspace/legal_research/agents/runner.py \
  --paper path/to/paper.txt \
  --intake /Users/main/Documents/workspace/legal_research/agents/paper_intake_template.md
```

### Running in create mode

```bash
python3 /Users/main/Documents/workspace/legal_research/agents/runner.py \
  --notes path/to/notes.txt \
  --intake /Users/main/Documents/workspace/legal_research/agents/paper_intake_template.md \
  --mode create
```

### Running just one agent

```bash
python3 /path/to/runner.py --paper paper.txt --intake intake.md --agent 1
```

Results are saved in `agents/reviews/YYYY-MM-DD_HH-MM/`.

---

## Adapting for a new paper

The agents are deliberately generic. To adapt for a specific paper:
- Describe the subfield clearly in the intake template
- If Agent 1's doctrinal expertise needs a specific addition (e.g. insolvency law, constitutional law), add one sentence to the intake's SPECIAL INSTRUCTIONS field
- Agent 2's checklist automatically skips empirical criteria for doctrinal papers — mark the paper type correctly in the intake

---

## Files

```
agents/
  README.md                    ← this file
  paper_intake_template.md     ← fill before every run
  agent1_doctrinal.md          ← Agent 1 system prompt
  agent2_methods.md            ← Agent 2 system prompt
  agent3_generalist.md         ← Agent 3 system prompt
  editor_synthesis.md          ← synthesis prompt (review mode only)
  runner.py                    ← API automation script
  reviews/                     ← outputs (created automatically)
    YYYY-MM-DD_HH-MM/
      agent1_review.md
      agent2_review.md
      agent3_review.md
      editor_synthesis.md      ← review mode
      final_draft.md           ← create mode
```
