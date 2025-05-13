## How to run

git clone 
exportexport LLM_API_URL=https://llm.srv.webis.de/api/chat
export LLM_MODEL=default

##make sure you are in agentic_story folder in terminal

python3 modules/pipeline/run_pipeline.py


## to do
1. test the params pass to LLM , its behavious record
2. create test case for workspace
3. create some agentic diagram
4. improve logging 
5. feedback and metric addition
6. 


tree
 tree
.
├── configs
│   ├── api_config.yml
│   └── logging.yml
├── data
│   ├── examples
│   │   └── sample_idea.txt
│   └── output
├── final_story.json
├── modules
│   ├── agents
│   │   ├── background
│   │   │   ├── background_agent.py
│   │   │   ├── prompts.py
│   │   │   └── __pycache__
│   │   │       ├── background_agent.cpython-312.pyc
│   │   │       └── prompts.cpython-312.pyc
│   │   ├── feedback
│   │   │   ├── feedback_agent.py
│   │   │   ├── prompts.py
│   │   │   └── __pycache__
│   │   │       ├── feedback_agent.cpython-312.pyc
│   │   │       └── prompts.cpython-312.pyc
│   │   ├── outline
│   │   │   ├── outline_agent.py
│   │   │   ├── prompts.py
│   │   │   └── __pycache__
│   │   │       ├── outline_agent.cpython-312.pyc
│   │   │       └── prompts.cpython-312.pyc
│   │   ├── persona
│   │   │   ├── persona_agent.py
│   │   │   ├── prompts.py
│   │   │   └── __pycache__
│   │   │       ├── persona_agent.cpython-312.pyc
│   │   │       └── prompts.cpython-312.pyc
│   │   ├── plot
│   │   │   ├── plot_agent.py
│   │   │   ├── prompts.py
│   │   │   └── __pycache__
│   │   │       ├── plot_agent.cpython-312.pyc
│   │   │       └── prompts.cpython-312.pyc
│   │   ├── revision
│   │   │   ├── prompts.py
│   │   │   ├── __pycache__
│   │   │   │   ├── prompts.cpython-312.pyc
│   │   │   │   └── revision_agent.cpython-312.pyc
│   │   │   └── revision_agent.py
│   │   ├── synthesis
│   │   │   ├── prompts.py
│   │   │   ├── __pycache__
│   │   │   │   ├── prompts.cpython-312.pyc
│   │   │   │   └── synthesis_agent.cpython-312.pyc
│   │   │   └── synthesis_agent.py
│   │   └── verification
│   │       ├── prompts.py
│   │       ├── __pycache__
│   │       │   ├── prompts.cpython-312.pyc
│   │       │   └── verification_agent.cpython-312.pyc
│   │       └── verification_agent.py
│   ├── clients
│   │   ├── llm_client.py
│   │   └── __pycache__
│   │       └── llm_client.cpython-312.pyc
│   ├── pipeline
│   │   └── run_pipeline.py
│   └── utils
│       └── io_utils.py
├── prompts
│   ├── background_agent.yml
│   ├── feedback_agent.yml
│   ├── outline_agent.yml
│   ├── persona_agent.yml
│   ├── plot_agent.yml
│   ├── revision_agent.yml
│   ├── synthesis_agent.yml
│   └── verification_agent.yml
├── README.md
├── requirements.txt
├── scripts
│   ├── deploy.sh
│   └── start_local.sh
└── tests
    ├── agents
    │   ├── test_background.py
    │   ├── test_feedback.py
    │   ├── test_outline.py
    │   ├── test_persona.py
    │   ├── test_plot.py
    │   ├── test_revision.py
    │   ├── test_synthesis.py
    │   └── test_verification.py
    ├── __init__.py
    ├── test_clients.py
    └── test_pipeline.py

31 directories, 63 files