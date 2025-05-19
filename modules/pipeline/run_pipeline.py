#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv
import tempfile
import subprocess
import json

# ———————————————————————
# Load .env and fix import path
# ———————————————————————
load_dotenv()
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# ———————————————————————
# Imports
# ———————————————————————
from modules.clients.llm_client import LLMClient
from modules.agents.background.background_agent import BackgroundAgent
from modules.agents.persona.persona_agent import PersonaAgent
from modules.agents.outline.outline_agent import OutlineAgent
from modules.agents.synthesis.synthesis_agent import SynthesisAgent
from modules.agents.plot.plot_agent import PlotAgent
from modules.agents.feedback.feedback_agent import FeedbackAgent
from modules.agents.revision.revision_agent import RevisionAgent
from modules.agents.verification.verification_agent import VerificationAgent

def prompt_edit(header: str, current: str) -> str:
    """
    Show the LLM output, then let the user either:
      • Press ENTER to keep it as-is
      • Type 'e' (and ENTER) to open it in $EDITOR for full multi-line editing
      • Or paste a one-line replacement directly
    """
    print(f"\n{'─'*60}\n{header}\n")
    print(current)
    print(f"\n{'─'*60}")
    choice = input("✏️  Press ENTER to accept, type 'e' to edit in editor, or paste replacement: ").strip()

    # 1) Inline replacement
    if choice and choice.lower() != 'e':
        return choice

    # 2) Open $EDITOR for full edit
    if choice.lower() == 'e':
        editor = os.getenv('EDITOR', 'vi')
        # Create a temp file populated with the current content
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode='w+') as tf:
            tf.write(current)
            tf.flush()
            # Launch your editor
            subprocess.call([editor, tf.name])
            tf.seek(0)
            edited = tf.read()
        # Clean up the temp file if you like:
        try:
            os.unlink(tf.name)
        except OSError:
            pass
        return edited

    # 3) Default (ENTER): keep as-is
    return current

def main():
    # ———————————————————————
    # Sanity check
    # ———————————————————————
    if not os.getenv("LLM_API_URL"):
        print("Error: Please set LLM_API_URL in your .env")
        sys.exit(1)

    # ———————————————————————
    # Initialize
    # ———————————————————————
    client = LLMClient()
    background_agent   = BackgroundAgent(client)
    persona_agent      = PersonaAgent(client)
    outline_agent      = OutlineAgent(client)
    synthesis_agent    = SynthesisAgent(client)
    plot_agent         = PlotAgent(client)
    feedback_agent     = FeedbackAgent(client)
    revision_agent     = RevisionAgent(client)
    verification_agent = VerificationAgent(client)

    idea = input("  Enter your story idea: ").strip()

    # 1) Background
    print("\n[1] Generating Background…")
    background = background_agent.generate_background(idea)
    background = prompt_edit(" Background (setting, mood, context):", background)

    # 2) Personas
    print("\n[2] Generating Personas…")
    personas = persona_agent.generate_personas(idea)
    personas = prompt_edit(" Personas (characters, arcs, conflicts):", personas)

    # 3) Outline
    print("\n[3] Generating Outline…")
    outline = outline_agent.generate_outline(idea)
    outline = prompt_edit(" Outline (3-act structure & key beats):", outline)

    # 4) Synthesis
    print("\n[4] Synthesizing Enriched Outline…")
    enriched_outline = synthesis_agent.synthesize(background, personas, outline)
    enriched_outline = prompt_edit(" Enriched Outline (integrated world, characters, plot):", enriched_outline)

    # 5) Draft
    print("\n[5] Expanding Outline to Draft…")
    draft = plot_agent.expand_outline(enriched_outline)
    draft = prompt_edit(" First Draft (full narrative):", draft)

    # 6) LLM Feedback
    print("\n[6] Gathering LLM Feedback…")
    llm_feedback = feedback_agent.get_llm_feedback(draft)
    print("\n LLM Feedback:\n")
    print(llm_feedback)

    # 7) Human Feedback
    print("\n  Enter your own feedback (type ‘END’ on its own line to finish):")
    human_lines = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        human_lines.append(line)
    human_feedback = "\n".join(human_lines)
    combined = f"LLM Feedback:\n{llm_feedback}\n\nHuman Feedback:\n{human_feedback}"
    combined = prompt_edit("🛠 Combined Feedback (edit before revision):", combined)

    # 8) Revision
    print("\n[7] Revising Draft…")
    revised = revision_agent.revise_story(draft, combined)
    revised = prompt_edit("✂️ Revised Story (final tweaks):", revised)

    # 9) Verification
    print("\n[8] Verifying Revised Story…")
    report = verification_agent.verify(revised)
    report = prompt_edit(" Verification Report (accept or adjust):", report)

    # Final Output
    print("\n === Final Story ===\n")
    print(revised)

    # Save the final story as JSON
    with open("final_story.json", "w") as f:
        json.dump({"story": revised}, f, indent=4)
    print("\n Final story saved to final_story.json")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n Exiting pipeline.")
        sys.exit(0)
