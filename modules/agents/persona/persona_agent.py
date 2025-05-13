from modules.clients.llm_client import LLMClient
from modules.agents.persona.prompts import load_persona_prompts


class PersonaAgent:
    """
    Agent responsible for generating detailed character profiles and arcs.
    """
    def __init__(self, client: LLMClient = None):
        self.client = client or LLMClient()
        self.system_prompt, self.user_template = load_persona_prompts()

    def generate_personas(self, idea: str) -> str:
        """
        Generate character profiles based on the story idea.

        :param idea: Story premise or idea
        :return: Character profiles and arcs
        """
        user_content = self.user_template.format(idea=idea)
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_content}
        ]
        personas = self.client.send(messages, stream=False)
        return personas
