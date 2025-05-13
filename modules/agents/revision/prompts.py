import os
import yaml


def load_revision_prompts():
    """
    Load the Revision Agent prompts from YAML definition.

    Expects a YAML file with keys:
      - system: system message template for revision
      - user: user message template with placeholders {story} and {feedback}
    """
    # Determine base directory (up three levels from this file)
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    print(base_dir)
    prompts_path = os.path.join(base_dir, 'prompts', 'revision_agent.yml')

    with open(prompts_path, 'r') as f:
        data = yaml.safe_load(f)

    system_prompt = data.get('system', '')
    user_template = data.get('user', '')
    return system_prompt, user_template
