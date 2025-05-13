import os
import yaml


def load_plot_prompts():
    """
    Load the Plot Agent prompts from YAML definition.

    Expects a YAML file with keys:
      - system: system message template
      - user: user message template with placeholder {outline}
    """
    # Determine base directory (up three levels from this file)
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    prompts_path = os.path.join(base_dir, 'prompts', 'plot_agent.yml')

    with open(prompts_path, 'r') as f:
        data = yaml.safe_load(f)

    system_prompt = data.get('system', '')
    user_template = data.get('user', '')
    return system_prompt, user_template
