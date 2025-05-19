import gradio as gr
import os
import json
import asyncio
import time
from dotenv import load_dotenv

# Load env and init agents
load_dotenv()

from modules.clients.llm_client import LLMClient
from modules.agents.background.background_agent import BackgroundAgent
from modules.agents.persona.persona_agent import PersonaAgent
from modules.agents.outline.outline_agent import OutlineAgent
from modules.agents.synthesis.synthesis_agent import SynthesisAgent
from modules.agents.plot.plot_agent import PlotAgent
from modules.agents.feedback.feedback_agent import FeedbackAgent
from modules.agents.revision.revision_agent import RevisionAgent
from modules.agents.verification.verification_agent import VerificationAgent

client = LLMClient()
background_agent = BackgroundAgent(client)
persona_agent = PersonaAgent(client)
outline_agent = OutlineAgent(client)
synthesis_agent = SynthesisAgent(client)
plot_agent = PlotAgent(client)
feedback_agent = FeedbackAgent(client)
revision_agent = RevisionAgent(client)
verification_agent = VerificationAgent(client)

async def run_stepwise_story_pipeline(idea, genre, tone, audience, uploaded_background, uploaded_personas,
                                       human_feedback_text, max_tokens, temperature, top_p, freq_penalty, pres_penalty):
    context_prefix = (
        f"Genre: {genre}\nTone: {tone}\nAudience: {audience}\nIdea: {idea}\n\n"
        f"Generation Settings:\n"
        f"max_tokens={max_tokens}, temperature={temperature}, top_p={top_p}, "
        f"frequency_penalty={freq_penalty}, presence_penalty={pres_penalty}"
    )
    timings = {}
    errors = []

    try:
        t0 = time.time()
        background_task = asyncio.create_task(
            asyncio.to_thread(background_agent.generate_background, context_prefix)
        )
        personas_task = asyncio.create_task(
            asyncio.to_thread(persona_agent.generate_personas, context_prefix)
        )

        outline = await asyncio.to_thread(outline_agent.generate_outline, context_prefix)
        timings["Outline"] = time.time() - t0

        t1 = time.time()
        background = uploaded_background if uploaded_background else await background_task
        personas = uploaded_personas if uploaded_personas else await personas_task
        timings["Background/Personas"] = time.time() - t1

        t2 = time.time()
        enriched_outline = await asyncio.to_thread(synthesis_agent.synthesize, background, personas, outline)
        timings["Synthesis"] = time.time() - t2

        t3 = time.time()
        draft = await asyncio.to_thread(plot_agent.expand_outline, enriched_outline)
        timings["Drafting"] = time.time() - t3

        t4 = time.time()
        llm_feedback = await asyncio.to_thread(feedback_agent.get_llm_feedback, draft)
        timings["LLM Feedback"] = time.time() - t4

        t5 = time.time()
        combined_feedback = f"LLM Feedback:\n{llm_feedback}\n\nHuman Feedback:\n{human_feedback_text}"
        revised = await asyncio.to_thread(revision_agent.revise_story, draft, combined_feedback)
        timings["Revision"] = time.time() - t5

        t6 = time.time()
        verification = await asyncio.to_thread(verification_agent.verify, revised)
        timings["Verification"] = time.time() - t6

        with open("final_story.json", "w") as f:
            json.dump({"story": revised}, f, indent=4)

        timing_report = "\n".join([f"{k}: {v:.2f}s" for k, v in timings.items()])
        return background, personas, outline, enriched_outline, draft, llm_feedback, revised, verification, "final_story.json", timing_report, ""

    except Exception as e:
        errors.append(str(e))
        return "", "", "", "", "", "", "", "", "", "", "\n".join(errors)

with gr.Blocks(title="Interactive Story Generator") as demo:
    gr.Markdown("#  Interactive Story Generator")

    with gr.Row():
        idea = gr.Textbox(label="Story Idea", placeholder="e.g., A robot discovers emotions", lines=2)
        genre = gr.Dropdown(["Fantasy", "Sci-Fi", "Mystery", "Romance", "Horror"], label="Genre")
        tone = gr.Dropdown(["Serious", "Comedic", "Dark", "Lighthearted"], label="Tone")
        audience = gr.Dropdown(["Adult", "Teen", "Kids"], label="Target Audience")

    with gr.Accordion("Optional: Upload Custom Background & Personas", open=False):
        uploaded_background = gr.Textbox(label="Custom Background", lines=6, placeholder="Paste background text...")
        uploaded_personas = gr.Textbox(label="Custom Personas", lines=6, placeholder="Paste character profiles...")

    with gr.Accordion(" Generation Settings", open=False):
        max_tokens = gr.Slider(100, 1000, value=350, step=50, label="Max Tokens")
        temperature = gr.Slider(0.0, 1.0, value=0.7, step=0.05, label="Temperature")
        top_p = gr.Slider(0.1, 1.0, value=0.9, step=0.05, label="Top-p")
        freq_penalty = gr.Slider(0.0, 2.0, value=0.0, step=0.1, label="Frequency Penalty")
        pres_penalty = gr.Slider(0.0, 2.0, value=0.0, step=0.1, label="Presence Penalty")

    human_feedback_text = gr.Textbox(label=" Human Feedback", placeholder="Your comments on the draft", lines=4)

    with gr.Row():
        run_button = gr.Button(" Generate Story")

    with gr.Tabs():
        with gr.Tab(" Background"):
            out_background = gr.Textbox(label="Generated Background", lines=10)
        with gr.Tab(" Personas"):
            out_personas = gr.Textbox(label="Generated Personas", lines=10)
        with gr.Tab(" Outline"):
            out_outline = gr.Textbox(label="Outline", lines=10)
        with gr.Tab(" Enriched Outline"):
            out_enriched = gr.Textbox(label="Enriched Outline", lines=10)
        with gr.Tab(" Draft"):
            out_draft = gr.Textbox(label="First Draft", lines=12)
        with gr.Tab(" LLM Feedback"):
            out_llm_feedback = gr.Textbox(label="LLM Feedback", lines=10)
        with gr.Tab(" Revised Story"):
            out_revised = gr.Textbox(label="Revised Story", lines=12)
        with gr.Tab(" Verification Report"):
            out_verification = gr.Textbox(label="Verification Report", lines=8)

    story_file = gr.File(label=" Download Final Story")
    timing_report = gr.Textbox(label=" Execution Time by Step", lines=8)
    error_output = gr.Textbox(label=" Errors (if any)", lines=4)

    run_button.click(
        fn=run_stepwise_story_pipeline,
        inputs=[
            idea, genre, tone, audience,
            uploaded_background, uploaded_personas,
            human_feedback_text,
            max_tokens, temperature, top_p, freq_penalty, pres_penalty
        ],
        outputs=[
            out_background, out_personas, out_outline, out_enriched,
            out_draft, out_llm_feedback, out_revised, out_verification,
            story_file, timing_report, error_output
        ]
    )

if __name__ == "__main__":
    demo.launch(share=True) # for accessing on other devices
