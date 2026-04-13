"""
Peer Review Runner — uses the Anthropic API to run all three agents
automatically on a paper file, then produces an editor synthesis.

SETUP (one-time):
  1. pip install anthropic
  2. Set your API key:  export ANTHROPIC_API_KEY="sk-ant-..."
     (or paste it directly into API_KEY below — but don't commit that to git)

USAGE:
  # Review mode (reviewing an existing paper):
  python runner.py --paper path/to/paper.txt --intake path/to/intake.md

  # Create mode (writing from notes):
  python runner.py --notes path/to/notes.txt --intake path/to/intake.md --mode create

  # Run a single agent only:
  python runner.py --paper path/to/paper.txt --intake path/to/intake.md --agent 1

OUTPUT:
  All reviews are saved in a timestamped folder:
  agents/reviews/YYYY-MM-DD_HH-MM/
    agent1_review.md
    agent2_review.md
    agent3_review.md
    editor_synthesis.md   (review mode only)
    final_draft.md        (create mode only)
"""

import os
import sys
import argparse
import datetime
from pathlib import Path

try:
    import anthropic
except ImportError:
    print("ERROR: anthropic package not installed. Run: pip install anthropic")
    sys.exit(1)

# ── Configuration ─────────────────────────────────────────────────────────────

AGENTS_DIR   = Path(__file__).parent
REVIEWS_DIR  = AGENTS_DIR / "reviews"
MODEL        = "claude-opus-4-6"          # best model for academic review
MAX_TOKENS   = 8000                       # per agent response

# Paste your API key here if you don't want to use an environment variable
# (but don't commit this file to git if you do!)
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")


# ── Load prompt files ─────────────────────────────────────────────────────────

def load_prompt(filename: str) -> str:
    path = AGENTS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    text = path.read_text(encoding="utf-8")
    # Extract content between the BEGIN/END PASTE markers
    start = text.find("## SYSTEM PROMPT — BEGIN PASTE HERE")
    end   = text.find("## SYSTEM PROMPT — END PASTE HERE")
    if start != -1 and end != -1:
        return text[start + len("## SYSTEM PROMPT — BEGIN PASTE HERE"):end].strip()
    return text  # fallback: use full file


def load_file(path: str) -> str:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if p.suffix == ".pdf":
        # Try to extract text from PDF using pdfplumber if available
        try:
            import pdfplumber
            pages = []
            with pdfplumber.open(p) as pdf:
                for page in pdf.pages:
                    t = page.extract_text()
                    if t:
                        pages.append(t)
            return "\n\n".join(pages)
        except ImportError:
            print("NOTE: pdfplumber not installed; cannot read PDF. Convert to .txt first.")
            sys.exit(1)
    return p.read_text(encoding="utf-8")


# ── Call the API ──────────────────────────────────────────────────────────────

def call_claude(system_prompt: str, user_message: str, label: str) -> str:
    if not API_KEY:
        print("ERROR: No API key found. Set ANTHROPIC_API_KEY environment variable.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=API_KEY)
    print(f"  Calling Claude ({label})... ", end="", flush=True)

    message = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    print("done.")
    return message.content[0].text


# ── Review workflow ───────────────────────────────────────────────────────────

def run_review(paper_text: str, intake_text: str, output_dir: Path, agents_to_run: list):
    base_message = f"{intake_text}\n\n---\n\n## PAPER TEXT\n\n{paper_text}"

    reviews = {}

    if 1 in agents_to_run:
        print("Running Agent 1 (Doctrinal & Theoretical)...")
        prompt = load_prompt("agent1_doctrinal.md")
        reviews[1] = call_claude(prompt, base_message, "Agent 1")
        (output_dir / "agent1_review.md").write_text(reviews[1], encoding="utf-8")
        print(f"  -> Saved: {output_dir / 'agent1_review.md'}")

    if 2 in agents_to_run:
        print("Running Agent 2 (Methods)...")
        prompt = load_prompt("agent2_methods.md")
        reviews[2] = call_claude(prompt, base_message, "Agent 2")
        (output_dir / "agent2_review.md").write_text(reviews[2], encoding="utf-8")
        print(f"  -> Saved: {output_dir / 'agent2_review.md'}")

    if 3 in agents_to_run:
        print("Running Agent 3 (Interdisciplinary)...")
        prompt = load_prompt("agent3_generalist.md")
        reviews[3] = call_claude(prompt, base_message, "Agent 3")
        (output_dir / "agent3_review.md").write_text(reviews[3], encoding="utf-8")
        print(f"  -> Saved: {output_dir / 'agent3_review.md'}")

    # Editor synthesis (only if all three ran)
    if set(agents_to_run) == {1, 2, 3} and len(reviews) == 3:
        print("Running Editor Synthesis...")
        prompt = load_prompt("editor_synthesis.md")
        combined = "\n\n---\n\n".join(
            [f"# AGENT {k} REVIEW\n\n{v}" for k, v in reviews.items()]
        )
        synthesis = call_claude(prompt, combined, "Editor")
        (output_dir / "editor_synthesis.md").write_text(synthesis, encoding="utf-8")
        print(f"  -> Saved: {output_dir / 'editor_synthesis.md'}")


# ── Create workflow (sequential: A1 → A2 → A3) ───────────────────────────────

def run_create(notes_text: str, intake_text: str, output_dir: Path):
    base_context = f"{intake_text}\n\n---\n\n## RESEARCH NOTES\n\n{notes_text}"

    # Agent 1: full first draft
    print("Running Agent 1 (first draft)...")
    prompt1 = load_prompt("agent1_doctrinal.md")
    draft1  = call_claude(prompt1, base_context, "Agent 1 — Create")
    (output_dir / "draft_v1_agent1.md").write_text(draft1, encoding="utf-8")
    print(f"  -> Saved: {output_dir / 'draft_v1_agent1.md'}")

    # Agent 2: methods revision
    print("Running Agent 2 (methods revision)...")
    prompt2   = load_prompt("agent2_methods.md")
    message2  = f"{base_context}\n\n---\n\n## AGENT 1 DRAFT\n\n{draft1}"
    draft2    = call_claude(prompt2, message2, "Agent 2 — Create")
    (output_dir / "draft_v2_agent2.md").write_text(draft2, encoding="utf-8")
    print(f"  -> Saved: {output_dir / 'draft_v2_agent2.md'}")

    # Agent 3: interdisciplinary enrichment + final draft
    print("Running Agent 3 (final enrichment)...")
    prompt3   = load_prompt("agent3_generalist.md")
    message3  = f"{base_context}\n\n---\n\n## AGENT 2 REVISED DRAFT\n\n{draft2}"
    draft3    = call_claude(prompt3, message3, "Agent 3 — Create")
    (output_dir / "final_draft.md").write_text(draft3, encoding="utf-8")
    print(f"  -> Saved: {output_dir / 'final_draft.md'}")

    print("\nCreation complete. Final draft: final_draft.md")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Peer review runner using Anthropic API")
    parser.add_argument("--paper",  help="Path to paper file (.txt or .pdf) — REVIEW mode")
    parser.add_argument("--notes",  help="Path to notes file (.txt) — CREATE mode")
    parser.add_argument("--intake", required=True, help="Path to filled-in paper_intake_template.md")
    parser.add_argument("--mode",   choices=["review", "create"], default="review")
    parser.add_argument("--agent",  type=int, choices=[1, 2, 3], help="Run a single agent only")
    args = parser.parse_args()

    # Create output directory
    timestamp  = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    output_dir = REVIEWS_DIR / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {output_dir}\n")

    intake_text = load_file(args.intake)
    agents_to_run = [args.agent] if args.agent else [1, 2, 3]

    if args.mode == "create":
        if not args.notes:
            print("ERROR: --notes required for create mode")
            sys.exit(1)
        notes_text = load_file(args.notes)
        run_create(notes_text, intake_text, output_dir)
    else:
        if not args.paper:
            print("ERROR: --paper required for review mode")
            sys.exit(1)
        paper_text = load_file(args.paper)
        run_review(paper_text, intake_text, output_dir, agents_to_run)

    print(f"\nAll done. Results saved in: {output_dir}")


if __name__ == "__main__":
    main()
