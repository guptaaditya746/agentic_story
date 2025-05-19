import os
import pytest
import yaml
from unittest.mock import MagicMock, patch

from modules.agents.background.background_agent import BackgroundAgent
from modules.agents.persona.persona_agent import PersonaAgent
from modules.agents.outline.outline_agent import OutlineAgent
from modules.agents.synthesis.synthesis_agent import SynthesisAgent
from modules.agents.plot.plot_agent import PlotAgent
from modules.agents.feedback.feedback_agent import FeedbackAgent
from modules.agents.revision.revision_agent import RevisionAgent
from modules.agents.verification.verification_agent import VerificationAgent

# Load the existing api_config.yml file
@pytest.fixture
def api_config():
    config_path = os.path.join(os.path.dirname(__file__), "..", "configs", "api_config.yml")
    assert os.path.exists(config_path), f"Config file not found at: {config_path}"
    return config_path


@pytest.fixture
def mock_llmclient_send():
    with patch('modules.clients.llm_client.LLMClient.send') as mock_send:
        yield mock_send

def test_background_agent_generate_background(mock_llmclient_send):
    mock_llmclient_send.return_value = "Background text about a dark forest."
    agent = BackgroundAgent()
    result = agent.generate_background("A haunted forest story")
    assert isinstance(result, str)
    assert "dark forest" in result or len(result) > 0

def test_persona_agent_generate_personas(mock_llmclient_send):
    mock_llmclient_send.return_value = "Character profiles: Alice, the brave heroine."
    agent = PersonaAgent()
    result = agent.generate_personas("A haunted forest story")
    assert isinstance(result, str)
    assert "Alice" in result

def test_outline_agent_generate_outline(mock_llmclient_send):
    mock_llmclient_send.return_value = "Act 1: Setup\nAct 2: Conflict\nAct 3: Resolution"
    agent = OutlineAgent()
    result = agent.generate_outline("A haunted forest story")
    assert isinstance(result, str)
    assert "Act 1" in result

def test_synthesis_agent_synthesize(mock_llmclient_send):
    mock_llmclient_send.return_value = "Synthesized draft combining background, personas, and outline."
    agent = SynthesisAgent()
    result = agent.synthesize("Background text", "Personas text", "Outline text")
    assert isinstance(result, str)
    assert "Synthesized" in result

def test_plot_agent_expand_outline(mock_llmclient_send):
    mock_llmclient_send.return_value = "Full narrative draft expanding the outline."
    agent = PlotAgent()
    result = agent.expand_outline("Outline text")
    assert isinstance(result, str)
    assert "narrative" in result

def test_feedback_agent_get_llm_feedback(mock_llmclient_send):
    mock_llmclient_send.return_value = "LLM feedback: The story could be more exciting."
    agent = FeedbackAgent()
    result = agent.get_llm_feedback("Draft story text")
    assert isinstance(result, str)
    assert "exciting" in result

def test_revision_agent_revise_story(mock_llmclient_send):
    mock_llmclient_send.return_value = "Revised story incorporating feedback."
    agent = RevisionAgent()
    result = agent.revise_story("Original story", "Feedback text")
    assert isinstance(result, str)
    assert "Revised" in result

def test_verification_agent_verify(mock_llmclient_send):
    mock_llmclient_send.return_value = "Verification report: No plot holes found."
    agent = VerificationAgent()
    result = agent.verify("Draft story text")
    assert isinstance(result, str)
    assert "No plot holes" in result

def test_feedback_agent_get_human_feedback(monkeypatch):
    inputs = iter([
        "Great story, but needs more action.",
        "Consider adding a new character.",
        "END"
    ])
    monkeypatch.setattr('builtins.input', lambda: next(inputs))
    agent = FeedbackAgent()
    feedback = agent.get_human_feedback()
    assert "Great story" in feedback
    assert "new character" in feedback
    assert "END" not in feedback

@pytest.mark.integration
def test_full_pipeline_run(mock_llmclient_send, monkeypatch, api_config):
    """
    Integration test simulating a full pipeline run.
    Each call to LLMClient.send returns a different canned response.
    """
    responses = {
        'background': "Background: spooky forest at night.",
        'personas': "Personas: Alice the heroine, Bob the villain.",
        'outline': "Outline: Act 1, Act 2, Act 3.",
        'synthesis': "Draft synthesized from background, personas, and outline.",
        'plot': "Expanded narrative draft.",
        'feedback': "LLM Feedback: Needs more suspense.",
        'revision': "Revised story with added suspense.",
        'verification': "Verification: Story is consistent."
    }

    # Set side_effect to return responses in order of calls
    mock_llmclient_send.side_effect = list(responses.values())

    # Monkeypatch human feedback input
    human_feedback_inputs = iter([
        "Add more vivid descriptions.",
        "END"
    ])
    monkeypatch.setattr('builtins.input', lambda: next(human_feedback_inputs))

    # Create agents
    background_agent = BackgroundAgent()
    persona_agent = PersonaAgent()
    outline_agent = OutlineAgent()
    synthesis_agent = SynthesisAgent()
    plot_agent = PlotAgent()
    feedback_agent = FeedbackAgent()
    revision_agent = RevisionAgent()
    verification_agent = VerificationAgent()

    # Simulate pipeline
    idea = "A haunted forest story"
    background = background_agent.generate_background(idea)
    personas = persona_agent.generate_personas(idea)
    outline = outline_agent.generate_outline(idea)
    draft = synthesis_agent.synthesize(background, personas, outline)
    expanded_story = plot_agent.expand_outline(outline)
    llm_feedback = feedback_agent.get_llm_feedback(expanded_story)
    human_feedback = feedback_agent.get_human_feedback()
    combined_feedback = llm_feedback + "\n" + human_feedback
    revised_story = revision_agent.revise_story(expanded_story, combined_feedback)
    verification_report = verification_agent.verify(revised_story)

    # Assertions for final outputs
    assert background == responses['background']
    assert personas == responses['personas']
    assert outline == responses['outline']
    assert draft == responses['synthesis']
    assert expanded_story == responses['plot']
    assert llm_feedback == responses['feedback']
    assert "Add more vivid descriptions." in human_feedback
    assert revised_story == responses['revision']
    assert verification_report == responses['verification']

    print("✅ Integration test passed: Full pipeline run.")
