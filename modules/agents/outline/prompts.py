import os
import yaml


def load_outline_prompts():
    """
    Load the Outline Agent prompts from YAML definition.

    Expects a YAML file with keys:
      - system: system message template
      - user: user message template with placeholder {idea}
    """
    # Determine path to prompts folder (relative to this file)
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) # Go up one more level
    prompts_path = os.path.join(base_dir, 'prompts', 'outline_agent.yml')

    with open(prompts_path, 'r') as f:
        data = yaml.safe_load(f)

    system_prompt = data.get('system', '')
    user_template = data.get('user', '')
    return system_prompt, user_template
