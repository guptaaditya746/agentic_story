#!/usr/bin/env python3
import os
import sys
import json
from dotenv import load_dotenv

# Load .env and fix import path
load_dotenv()
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Imports
from modules.clients.llm_client import LLMClient
from modules.agents.background.background_agent import BackgroundAgent
from modules.agents.persona.persona_agent import PersonaAgent
from modules.agents.outline.outline_agent import OutlineAgent
from modules.agents.synthesis.synthesis_agent import SynthesisAgent
from modules.agents.plot.plot_agent import PlotAgent
from modules.agents.feedback.feedback_agent import FeedbackAgent
from modules.agents.revision.revision_agent import RevisionAgent
from modules.agents.verification.verification_agent import VerificationAgent

def run_story_pipeline(idea: str) -> dict:
    client = LLMClient()
    background_agent   = BackgroundAgent(client)
    persona_agent      = PersonaAgent(client)
    outline_agent      = OutlineAgent(client)
    synthesis_agent    = SynthesisAgent(client)
    plot_agent         = PlotAgent(client)
    feedback_agent     = FeedbackAgent(client)
    revision_agent     = RevisionAgent(client)
    verification_agent = VerificationAgent(client)

    print("🔧 Step 1: Generating Background...")
    background = background_agent.generate_background(idea)

    print("🔧 Step 2: Generating Personas...")
    personas = persona_agent.generate_personas(idea)

    print("🔧 Step 3: Generating Outline...")
    outline = outline_agent.generate_outline(idea)

    print("🔧 Step 4: Synthesizing Enriched Outline...")
    enriched_outline = synthesis_agent.synthesize(background, personas, outline)

    print("🔧 Step 5: Expanding Outline to Draft...")
    draft = plot_agent.expand_outline(enriched_outline)

    print("🔧 Step 6: Getting LLM Feedback...")
    llm_feedback = feedback_agent.get_llm_feedback(draft)
    human_feedback = ""  # Skipped
    combined_feedback = f"LLM Feedback:\n{llm_feedback}\n\nHuman Feedback:\n{human_feedback}"

    print("🔧 Step 7: Revising Draft...")
    revised = revision_agent.revise_story(draft, combined_feedback)

    print("🔧 Step 8: Verifying Story...")
    verification = verification_agent.verify(revised)

    print("✅ All steps completed.\n")
    return {
        "idea": idea,
        "background": background,
        "personas": personas,
        "outline": outline,
        "enriched_outline": enriched_outline,
        "draft": draft,
        "llm_feedback": llm_feedback,
        "human_feedback": human_feedback,
        "combined_feedback": combined_feedback,
        "revised_story": revised,
        "verification_report": verification
    }


def main():
    input_file = "./notebook/story_prompts.json"
    output_file = "final_stories.json"

    with open(input_file, "r") as f:
        prompt_list = json.load(f)

    all_results = []

    for item in prompt_list:
        story_id = item["story_id"]
        prompts = item["prompts"]
        lang = item.get("lang", "en")
        idea = f"{prompts['INTRO']}. {prompts['SECTION']}. {prompts['OUTRO']}."
        print(f"\n🚀 Generating story for {story_id}: {idea}")

        try:
            outputs = run_story_pipeline(idea)

            # Save the revised story to a .txt file
            story_text = outputs.get("revised_story", "")
            txt_filename = f"{story_id}.txt"
            with open(txt_filename, "w", encoding="utf-8") as txt_file:
                txt_file.write(story_text)
            
            all_results.append({
                "story_id": story_id,
                "lang": lang,
                "prompts": prompts,
                "outputs": outputs
            })
        except Exception as e:
            print(f"❌ Error processing {story_id}: {e}")
            all_results.append({
                "story_id": story_id,
                "lang": lang,
                "prompts": prompts,
                "error": str(e)
            })

    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\n✅ All stories saved to {output_file}")

if __name__ == "__main__":
    main()
