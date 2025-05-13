# modules/clients/llm_client.py

import os
import json
import requests
import yaml

from dotenv import load_dotenv
from requests.exceptions import JSONDecodeError

# Load .env into os.environ (so env vars override YAML)
load_dotenv()


class LLMClient:
    """
    A thin wrapper over the LLM API endpoint, supporting both blocking and streaming modes.
    Reads defaults from agentic_story/configs/api_config.yml, with ENV override.
    Supports per-call overrides for generation parameters.
    """
    def __init__(self, config_path: str = None):
        # Determine config file
        if config_path:
            cfg_path = config_path
        elif os.getenv("API_CONFIG_PATH"):
            cfg_path = os.getenv("API_CONFIG_PATH")
        else:
            # Default path: <project_root>/configs/api_config.yml
            llm_client_file_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up two levels from .../modules/clients/ to .../agentic_story/
            project_root = os.path.abspath(
                os.path.join(llm_client_file_dir, os.pardir, os.pardir)
            )
            cfg_path = os.path.join(project_root, "configs", "api_config.yml")

        with open(cfg_path, "r") as f:
            cfg = yaml.safe_load(f)

        # LLM API settings
        api_cfg = cfg.get("llm_api", {})
        self.api_url = os.getenv("LLM_API_URL", api_cfg.get("url"))
        self.model = os.getenv("LLM_MODEL", api_cfg.get("model", "default"))
        self.timeout = api_cfg.get("timeout", 60)
        self.default_stream = api_cfg.get("stream", False)

        # Generation defaults
        gen_cfg = cfg.get("generation", {})
        self.gen_defaults = {
            key: gen_cfg[key]
            for key in (
                "max_tokens",
                "temperature",
                "top_p",
                "frequency_penalty",
                "presence_penalty",
            )
            if key in gen_cfg
        }

        if not self.api_url:
            raise ValueError("LLM_API_URL must be set via env or api_config.yml")

    def send(
        self,
        messages: list,
        stream: bool = None,
        max_tokens: int = None,
        temperature: float = None,
        top_p: float = None,
        frequency_penalty: float = None,
        presence_penalty: float = None,
        **extra_kwargs
    ) -> str:
        """
        Send a chat payload.
        - If stream=False, returns the full assistant response (handles JSON or NDJSON).
        - If stream=True, prints and returns streamed content.
        - If stream is None, uses the default from api_config.yml.
        - Per-call overrides for generation params are accepted.
        """
        use_stream = self.default_stream if stream is None else stream

        # Build payload with defaults
        payload = {
            "model": self.model,
            "messages": messages,
            **self.gen_defaults,
        }

        # Override defaults if args provided
        overrides = {
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
        }
        for param, val in overrides.items():
            if val is not None:
                payload[param] = val

        # Include any additional kwargs (e.g., stop sequences)
        payload.update(extra_kwargs)

        headers = {"Content-Type": "application/json"}
        response = requests.post(
            self.api_url,
            json=payload,
            headers=headers,
            stream=use_stream,
            timeout=self.timeout,
        )
        response.raise_for_status()

        if use_stream:
            return self._stream_response(response)

        # Non-streaming: try single JSON parse
        try:
            data = response.json()
            return self._extract_content(data)
        except JSONDecodeError:
            # Fallback: handle NDJSON lines
            full_content = []
            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    continue
                try:
                    chunk = json.loads(line)
                except json.JSONDecodeError:
                    continue

                # Extract content
                content = None
                if "message" in chunk and isinstance(chunk["message"], dict):
                    content = chunk["message"].get("content")
                elif "choices" in chunk:
                    try:
                        content = chunk["choices"][0]["message"]["content"]
                    except (KeyError, IndexError):
                        content = None

                if content:
                    full_content.append(content)
            return "".join(full_content).strip()

    def _stream_response(self, response) -> str:
        """
        Internal: iterate over response.iter_lines(), parse JSON chunks, print and accumulate.
        """
        full_content = []
        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue
            try:
                chunk = json.loads(line)
            except json.JSONDecodeError:
                continue
            msg = chunk.get("message", {})
            content = msg.get("content")
            if content:
                print(content, end="", flush=True)
                full_content.append(content)
            if chunk.get("done", False) or chunk.get("done_reason"):
                break
        print()
        return "".join(full_content).strip()

    def _extract_content(self, data: dict) -> str:
        """
        Extract content from a parsed JSON response dict.
        Supports both 'message' and 'choices' formats.
        """
        if "message" in data and isinstance(data["message"], dict):
            content = data["message"].get("content")
            if content is not None:
                return content.strip()

        if "choices" in data:
            try:
                return data["choices"][0]["message"]["content"].strip()
            except (KeyError, IndexError, TypeError):
                pass

        raise ValueError(f"Unexpected response format: {json.dumps(data)}")
