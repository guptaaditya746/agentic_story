from modules.clients.llm_client import LLMClient
from modules.agents.outline.prompts import load_outline_prompts


class OutlineAgent:
    """
    Agent responsible for generating a structured story outline.
    """
    def __init__(self, client: LLMClient = None):
        # Initialize LLM client (reads env vars if not provided)
        self.client = client or LLMClient()
        # Load system and user prompt templates
        self.system_prompt, self.user_template = load_outline_prompts()

    def generate_outline(self, idea: str) -> str:
        """
        Generate a three-act story outline based on the provided idea.

        :param idea: High-level story idea/premise
        :return: Outline text
        """
        user_content = self.user_template.format(idea=idea)
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_content}
        ]
        # We don't need streaming here; outline is returned in one go
        outline = self.client.send(messages, stream=False, max_tokens=2048)
        return outline
