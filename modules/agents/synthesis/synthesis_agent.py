import os
from modules.clients.llm_client import LLMClient
from modules.agents.synthesis.prompts import load_synthesis_prompts

class SynthesisAgent:
    """
    Agent responsible for synthesizing background, personas, and outline into a cohesive draft.
    """
    def __init__(self, client: LLMClient = None):
        self.client = client or LLMClient()
        self.system_prompt, self.user_template = load_synthesis_prompts()

    def synthesize(self, background: str, personas: str, outline: str) -> str:
        """
        Generate a synthesized draft combining background, character personas, and plot outline.

        :param background: Background description text
        :param personas: Character profiles text
        :param outline: Structured outline text
        :return: Synthesized draft story text
        """
        user_content = self.user_template.format(
            background=background,
            personas=personas,
            outline=outline
        )
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_content}
        ]
        draft = self.client.send(messages, stream=False)
        return draft