from modules.clients.llm_client import LLMClient
from modules.agents.background.prompts import load_background_prompts

class BackgroundAgent:
    """
    Agent responsible for generating the story's background and setting details.
    """
    def __init__(self, client: LLMClient = None):
        self.client = client or LLMClient()
        self.system_prompt, self.user_template = load_background_prompts()

    def generate_background(self, idea: str) -> str:
        """
        Generate background description (time, place, mood) for the given story idea.

        :param idea: Story premise or idea
        :return: Background description text
        """
        user_content = self.user_template.format(idea=idea)
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_content}
        ]
        background = self.client.send(messages, stream=False)
        return background
