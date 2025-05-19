import pytest
import requests
import requests_mock
import os
from modules.clients.llm_client import LLMClient

# Helper function to set environment variables for testing
def set_test_env():
    os.environ["LLM_API_URL"] = "http://test-api.local"
    os.environ["LLM_MODEL"] = "test-model"

# Unit Tests for LLMClient Initialization
def test_init_with_default_path():
    set_test_env()
    client = LLMClient()
    assert client.api_url == "http://test-api.local"
    assert client.model == "test-model"

def test_init_with_custom_path():
    client = LLMClient(config_path="configs/test_api_config.yml")
    assert client.api_url == "http://test-api.local"

def test_init_without_url():
    # Remove both the environment variable and the config entry
    os.environ.pop("LLM_API_URL", None)
    # Create a minimal config file without the URL
    empty_config_path = "configs/empty_test_api_config.yml"
    with open(empty_config_path, "w") as f:
        f.write("llm_api: {}\n")

    try:
        client = LLMClient(config_path=empty_config_path)
    except ValueError:
        assert True  # Expected behavior
    else:
        assert False, "Expected ValueError for missing LLM_API_URL"



# Mocking API Responses
@pytest.fixture
def mock_response():
    return {
        "message": {
            "content": "Test response"
        }
    }

# Mocked API Test (Non-Streaming)
def test_send_request_non_streaming(mock_response):
    set_test_env()
    client = LLMClient()
    messages = [{"role": "user", "content": "Hello"}]

    with requests_mock.Mocker() as m:
        m.post(client.api_url, json=mock_response)
        response = client.send(messages)
        assert response == "Test response"

# Mocked API Test (Streaming)
def test_send_request_streaming(mock_response):
    set_test_env()
    client = LLMClient()
    messages = [{"role": "user", "content": "Stream"}]

    with requests_mock.Mocker() as m:
        m.post(client.api_url, text='{"message": {"content": "Streamed response"}}\n', headers={"Content-Type": "application/json"})
        response = client.send(messages, stream=True)
        assert "Streamed response" in response

# Test Handling of Invalid JSON Response
def test_invalid_json_response():
    set_test_env()
    client = LLMClient()
    messages = [{"role": "user", "content": "Invalid"}]

    with requests_mock.Mocker() as m:
        m.post(client.api_url, text="Not a JSON")
        # The method should handle the error internally and not raise an exception
        response = client.send(messages)
        assert response == "", "Expected an empty string as response when JSON is invalid"



# Test Timeout Handling
def test_request_timeout():
    set_test_env()
    client = LLMClient()
    messages = [{"role": "user", "content": "Timeout"}]

    with requests_mock.Mocker() as m:
        m.post(client.api_url, exc=requests.Timeout)
        with pytest.raises(requests.Timeout):
            client.send(messages)

# Test with Missing Message Content
def test_missing_message_content():
    set_test_env()
    client = LLMClient()
    messages = [{"role": "user", "content": None}]

    with requests_mock.Mocker() as m:
        m.post(client.api_url, json={"choices": [{"message": {}}]})
        with pytest.raises(ValueError):
            client.send(messages)


# Integration Test (Assuming a Mock Server)
@pytest.mark.integration
def test_integration_with_mock_server():
    set_test_env()
    client = LLMClient()
    messages = [{"role": "user", "content": "Integration Test"}]

    with requests_mock.Mocker() as m:
        m.post(client.api_url, json={"message": {"content": "Integration response"}})
        response = client.send(messages)
        assert response == "Integration response"
