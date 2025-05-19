import pytest
import json
import builtins
from unittest.mock import MagicMock, patch
from modules.pipeline.auto_story_batch import run_story_pipeline, main

@pytest.fixture
def mock_agents():
    with patch("modules.pipeline.auto_story_batch.LLMClient") as mock_client, \
         patch("modules.pipeline.auto_story_batch.BackgroundAgent") as MockBackgroundAgent, \
         patch("modules.pipeline.auto_story_batch.PersonaAgent") as MockPersonaAgent, \
         patch("modules.pipeline.auto_story_batch.OutlineAgent") as MockOutlineAgent, \
         patch("modules.pipeline.auto_story_batch.SynthesisAgent") as MockSynthesisAgent, \
         patch("modules.pipeline.auto_story_batch.PlotAgent") as MockPlotAgent, \
         patch("modules.pipeline.auto_story_batch.FeedbackAgent") as MockFeedbackAgent, \
         patch("modules.pipeline.auto_story_batch.RevisionAgent") as MockRevisionAgent, \
         patch("modules.pipeline.auto_story_batch.VerificationAgent") as MockVerificationAgent:
        
        # Create mocked instances
        mock_client_instance = mock_client.return_value
        background_instance = MockBackgroundAgent.return_value
        persona_instance = MockPersonaAgent.return_value
        outline_instance = MockOutlineAgent.return_value
        synthesis_instance = MockSynthesisAgent.return_value
        plot_instance = MockPlotAgent.return_value
        feedback_instance = MockFeedbackAgent.return_value
        revision_instance = MockRevisionAgent.return_value
        verification_instance = MockVerificationAgent.return_value

        # Define fake responses
        background_instance.generate_background.return_value = "Mock Background"
        persona_instance.generate_personas.return_value = "Mock Personas"
        outline_instance.generate_outline.return_value = "Mock Outline"
        synthesis_instance.synthesize.return_value = "Mock Enriched Outline"
        plot_instance.expand_outline.return_value = "Mock Draft"
        feedback_instance.get_llm_feedback.return_value = "Mock LLM Feedback"
        revision_instance.revise_story.return_value = "Mock Revised Story"
        verification_instance.verify.return_value = "Mock Verification Report"
        
        yield {
            "background": background_instance,
            "personas": persona_instance,
            "outline": outline_instance,
            "synthesis": synthesis_instance,
            "plot": plot_instance,
            "feedback": feedback_instance,
            "revision": revision_instance,
            "verification": verification_instance
        }


@pytest.mark.parametrize("idea", [
    "A story about space exploration",
    "A medieval fantasy adventure",
    "An AI learning to write stories"
])
def test_run_story_pipeline(mock_agents, idea):
    # Run the story pipeline with a mock idea
    result = run_story_pipeline(idea)

    # Check if the result contains all expected keys
    expected_keys = [
        "idea", "background", "personas", "outline", "enriched_outline",
        "draft", "llm_feedback", "human_feedback", "combined_feedback",
        "revised_story", "verification_report"
    ]
    assert all(key in result for key in expected_keys)

    # Check if the mock values are returned as expected
    assert result["background"] == "Mock Background"
    assert result["personas"] == "Mock Personas"
    assert result["outline"] == "Mock Outline"
    assert result["enriched_outline"] == "Mock Enriched Outline"
    assert result["draft"] == "Mock Draft"
    assert result["llm_feedback"] == "Mock LLM Feedback"
    assert result["revised_story"] == "Mock Revised Story"
    assert result["verification_report"] == "Mock Verification Report"


def test_main(monkeypatch, tmp_path):
    original_open = builtins.open  # save original open
    
    # create temp files etc
    input_file = tmp_path / "story_prompts.json"
    output_file = tmp_path / "final_stories.json"

    story_data = [
        {
            "story_id": "test_story_1",
            "prompts": {"INTRO": "A new beginning", "SECTION": "A challenge", "OUTRO": "A resolution"},
            "lang": "en"
        }
    ]
    with original_open(input_file, "w") as f:
        json.dump(story_data, f)

    # monkeypatch 'open' with a lambda that calls original_open
    def open_mock(f, *args, **kwargs):
        if "story_prompts.json" in str(f):
            return original_open(input_file, *args, **kwargs)
        else:
            return original_open(output_file, *args, **kwargs)

    monkeypatch.setattr("builtins.open", open_mock)

    # monkeypatch run_story_pipeline as before
    monkeypatch.setattr(
        "modules.pipeline.auto_story_batch.run_story_pipeline",
        lambda x: {
            "revised_story": "Test Story",
            "verification_report": "Verified"
        }
    )

    # Run main
    main()

    # Verify output
    with original_open(output_file, "r") as f:
        results = json.load(f)

    assert len(results) == 1
    assert results[0]["story_id"] == "test_story_1"
    assert "outputs" in results[0]
    assert results[0]["outputs"]["revised_story"] == "Test Story"
    assert results[0]["outputs"]["verification_report"] == "Verified"



def test_run_story_pipeline_error(mock_agents):
    # Simulate an exception in the background generation step
    mock_agents["background"].generate_background.side_effect = Exception("Background generation failed")

    with pytest.raises(Exception, match="Background generation failed"):
        run_story_pipeline("An idea that fails")
