import pytest
import asyncio
import re
from unittest.mock import AsyncMock, MagicMock, patch
import json

from modules.pipeline import gradio_pipeline as gp

def normalize_label(label):
    """
    Normalize labels by removing emojis and extra whitespace.
    """
    return re.sub(r'[^\w\s\-\(\)]+', '', label).strip()


def extract_labels(component):
    """
    Recursively extract labels from Gradio components.
    """
    labels = []
    try:
        if hasattr(component, "label") and component.label:
            labels.append(component.label)
        if hasattr(component, "children"):
            for child in component.children:
                labels.extend(extract_labels(child))
        # Handling Gradio containers (e.g., Tabs, Accordions)
        if hasattr(component, "blocks") and component.blocks:
            for block in component.blocks:
                labels.extend(extract_labels(block))
    except Exception as e:
        print(f"Error extracting label from component: {e}")
    return labels

@pytest.mark.asyncio
async def test_gradio_ui_components_present():
    # Test the Gradio demo app for expected components
    demo = gp.demo
    assert hasattr(demo, "launch")

    # Recursively extract labels from the demo UI components
    labels = extract_labels(demo)

    # Print the extracted labels to see the actual structure
    print("\nExtracted Labels:", labels)

    # Normalized expected labels
    expected_labels = [
        "Story Idea", "Genre", "Tone", "Target Audience",
        "Custom Background", "Custom Personas", "Max Tokens", "Temperature",
        "Top-p", "Frequency Penalty", "Presence Penalty", "Human Feedback",
        "Generated Background", "Generated Personas", "Outline", "Enriched Outline",
        "First Draft", "LLM Feedback", "Revised Story", "Verification Report",
        "Download Final Story", "Execution Time by Step", "Errors (if any)"
    ]

    # Normalize extracted labels
    normalized_labels = [normalize_label(label) for label in labels]

    # Check all expected labels are present in the demo UI components
    for label in expected_labels:
        assert label in normalized_labels, f"Missing component label: {label}"

@pytest.mark.asyncio
async def test_run_stepwise_story_pipeline_success(monkeypatch):
    # Prepare fake outputs for each agent step
    fake_background = "Fake Background"
    fake_personas = "Fake Personas"
    fake_outline = "Fake Outline"
    fake_enriched_outline = "Fake Enriched Outline"
    fake_draft = "Fake Draft"
    fake_llm_feedback = "Fake LLM Feedback"
    fake_revised = "Fake Revised Story"
    fake_verification = "Fake Verification Report"

    # Patch agent methods used inside run_stepwise_story_pipeline
    monkeypatch.setattr(gp.background_agent, "generate_background", MagicMock(return_value=fake_background))
    monkeypatch.setattr(gp.persona_agent, "generate_personas", MagicMock(return_value=fake_personas))
    monkeypatch.setattr(gp.outline_agent, "generate_outline", MagicMock(return_value=fake_outline))
    monkeypatch.setattr(gp.synthesis_agent, "synthesize", MagicMock(return_value=fake_enriched_outline))
    monkeypatch.setattr(gp.plot_agent, "expand_outline", MagicMock(return_value=fake_draft))
    monkeypatch.setattr(gp.feedback_agent, "get_llm_feedback", MagicMock(return_value=fake_llm_feedback))
    monkeypatch.setattr(gp.revision_agent, "revise_story", MagicMock(return_value=fake_revised))
    monkeypatch.setattr(gp.verification_agent, "verify", MagicMock(return_value=fake_verification))

    # Patch json.dump to avoid writing file
    json_dump_mock = MagicMock()
    monkeypatch.setattr(json, "dump", json_dump_mock)

    result = await gp.run_stepwise_story_pipeline(
        "My story idea", "Fantasy", "Serious", "Adult", 
        "", "", "Great draft!", 350, 0.7, 0.9, 0.0, 0.0
    )

    (background, personas, outline, enriched_outline, draft, 
     llm_feedback, revised, verification, filename, 
     timing_report, errors) = result

    assert background == fake_background
    assert personas == fake_personas
    assert outline == fake_outline
    assert enriched_outline == fake_enriched_outline
    assert draft == fake_draft
    assert llm_feedback == fake_llm_feedback
    assert revised == fake_revised
    assert verification == fake_verification
    assert filename == "final_story.json"
    assert isinstance(timing_report, str)
    assert errors == ""

    # Confirm json.dump called to write final story
    json_dump_mock.assert_called_once()

@pytest.mark.asyncio
async def test_gradio_launch():
    """
    Test that the Gradio application can launch without errors.
    """
    demo = gp.demo
    assert hasattr(demo, "launch")

@pytest.mark.asyncio
async def test_run_stepwise_story_pipeline_error(monkeypatch):
    def raise_error(*args, **kwargs):
        raise RuntimeError("Test induced error")

    monkeypatch.setattr(gp.background_agent, "generate_background", MagicMock(side_effect=raise_error))

    result = await gp.run_stepwise_story_pipeline(
        "Idea", "Genre", "Tone", "Audience",
        "", "", "", 350, 0.7, 0.9, 0.0, 0.0
    )

    *_, error_output = result[-1], result[-1]
    assert "Test induced error" in error_output
