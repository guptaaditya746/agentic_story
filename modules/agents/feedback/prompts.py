import os
import yaml


def load_feedback_prompts():
    """
    Load the Feedback Agent prompts from YAML definition.

    Expects a YAML file with keys:
      - system: system message template for LLM feedback
      - user: user message template with placeholder {story}
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    prompts_path = os.path.join(base_dir, 'prompts', 'feedback_agent.yml')

    with open(prompts_path, 'r') as f:
        data = yaml.safe_load(f)

    system_prompt = data.get('system', '')
    user_template = data.get('user', '')
    return system_prompt, user_template
