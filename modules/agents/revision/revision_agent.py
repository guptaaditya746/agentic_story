from modules.clients.llm_client import LLMClient
from modules.agents.revision.prompts import load_revision_prompts


class RevisionAgent:
    """
    Agent responsible for revising the story draft based on combined feedback.
    """
    def __init__(self, client: LLMClient = None):
        self.client = client or LLMClient()
        # Load system and user prompt templates
        self.system_prompt, self.user_template = load_revision_prompts()

    def revise_story(self, story: str, feedback: str) -> str:
        """
        Generate a revised version of the story draft, incorporating feedback.

        :param story: Original story draft
        :param feedback: Combined LLM and human feedback
        :return: Revised story text
        """
        # Format user message with both story and feedback
        user_content = self.user_template.format(story=story, feedback=feedback)
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_content}
        ]
        # Return full revised story in one response
        revised = self.client.send(messages, stream=False)
        return revised
