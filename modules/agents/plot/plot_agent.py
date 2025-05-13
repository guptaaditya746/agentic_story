from modules.clients.llm_client import LLMClient
from modules.agents.plot.prompts import load_plot_prompts


class PlotAgent:
    """
    Agent responsible for expanding a story outline into a full narrative.
    """
    def __init__(self, client: LLMClient = None):
        # Initialize LLM client (reads env vars if not provided)
        self.client = client or LLMClient()
        # Load system and user prompt templates
        self.system_prompt, self.user_template = load_plot_prompts()

    def expand_outline(self, outline: str) -> str:
        """
        Generate a narrative based on the provided outline.

        :param outline: Structured story outline text
        :return: Draft story text
        """
        user_content = self.user_template.format(outline=outline)
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_content}
        ]
        # Returning full story in one response
        story = self.client.send(messages, stream=False)
        return story