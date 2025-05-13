from modules.clients.llm_client import LLMClient
from modules.agents.feedback.prompts import load_feedback_prompts


class FeedbackAgent:
    """
    Agent responsible for obtaining LLM feedback and facilitating human feedback collection.
    """
    def __init__(self, client: LLMClient = None):
        # Initialize LLM client
        self.client = client or LLMClient()
        # Load prompts
        self.system_prompt, self.user_template = load_feedback_prompts()

    def get_llm_feedback(self, story: str) -> str:
        """
        Use the LLM to critique the provided story draft.

        :param story: The draft story text
        :return: Feedback text from the LLM
        """
        user_content = self.user_template.format(story=story)
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_content}
        ]
        feedback = self.client.send(messages, stream=False)
        return feedback

    def get_human_feedback(self) -> str:
        """
        Prompt user via CLI to enter human feedback line by line. Terminates on 'END'.

        :return: Concatenated human feedback
        """
        print("\n--- Human Feedback ---")
        lines = []
        print("Enter your feedback. Type 'END' on a new line to finish.")
        while True:
            try:
                line = input()
            except EOFError:
                break
            if line.strip().upper() == 'END':
                break
            lines.append(line)
        return "\n".join(lines)
