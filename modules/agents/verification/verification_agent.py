from modules.clients.llm_client import LLMClient
from modules.agents.verification.prompts import load_verification_prompts

class VerificationAgent:
    """
    Agent responsible for verifying consistency and coherence in the story draft.
    """
    def __init__(self, client: LLMClient = None):
        self.client = client or LLMClient()
        self.system_prompt, self.user_template = load_verification_prompts()

    def verify(self, draft: str) -> str:
        """
        Analyze the story draft for continuity, timeline consistency, and plot holes.

        :param draft: The story draft text
        :return: Verification report with issues and suggestions
        """
        user_content = self.user_template.format(draft=draft)
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_content}
        ]
        report = self.client.send(messages, stream=False)
        return report
