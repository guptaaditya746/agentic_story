import pytest
import json
import os
from modules.pipeline.auto_story_batch import run_story_pipeline, main

# Set environment variables to support ${...} in YAML
@pytest.fixture(scope="session", autouse=True)
def set_env_vars():
    os.environ["LLM_API_URL"] = "https://llm.srv.webis.de/api/chat"
    os.environ["LLM_MODEL"] = "default"

@pytest.mark.parametrize("idea", [
    "A story about space exploration",
    "A medieval fantasy adventure",
    "An AI learning to write stories"
])
def test_run_story_pipeline_real(idea):
    result = run_story_pipeline(idea)

    expected_keys = [
        "idea", "background", "personas", "outline", "enriched_outline",
        "draft", "llm_feedback", "human_feedback", "combined_feedback",
        "revised_story", "verification_report"
    ]
    for key in expected_keys:
        assert key in result
        assert isinstance(result[key], str) or result[key] is None

    print("\n\nGenerated Result for Idea:", idea)
    for key in expected_keys:
        print(f"{key}: {result[key]}\n")


def test_main(tmp_path, monkeypatch):
    # Create sample input file
    input_file = tmp_path / "story_prompts.json"
    output_file = tmp_path / "final_stories.json"

    sample_prompts = [{
        "story_id": "test_001",
        "prompts": {
            "INTRO": "An alien crash lands on Earth.",
            "SECTION": "Humans try to help.",
            "OUTRO": "The alien returns home."
        },
        "lang": "en"
    }]

    with open(input_file, "w") as f:
        json.dump(sample_prompts, f)

    # Patch sys.argv-like behavior by monkeypatching __file__ references in main()
    monkeypatch.setattr("sys.argv", ["auto_story_batch.py", str(input_file), str(output_file)])

    # Call main pipeline
    main()

    # Validate result
    with open(output_file, "r") as f:
        results = json.load(f)

    assert len(results) == 1
    assert results[0]["story_id"] == "test_001"
    assert "outputs" in results[0]
    assert "revised_story" in results[0]["outputs"]
    assert "verification_report" in results[0]["outputs"]
