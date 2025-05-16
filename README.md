```markdown

### TODO
1. test the params pass to LLM , its behavious record [adi][in progress]
2. create test case for workspace [rizvi]
3. add workflow diagram in readme [adi][gemacht] 
4. improve logging [rizvi]
5. feedback and metric addition [adi][gemacht]
5.1. add feedback which you are using under : agentic_story/tools/ [rizvi]
5.2. add TACCO and SEANCE, different python versions [adi]
6. use prompts_story.json to generate stories for analysis [adi][gemacht]
7. add simple gui using Gradio for mock presentation [adi]
8. add framework for prompts , add P2 (check google sheets) [adi]
9. add benchmarking [adi]

### Observations
1. giving precise feedback works
2. even though context widnow of llm (webis) is big, but for better quality it 
shoudl be under some limit (i dont know how to find this limit), 
so some form keyword or summarise agent in loop/in b/w agents , may work



# Agentic Story Pipeline

A modular, agent-based pipeline for interactive story generation with human–LLM collaboration. This project orchestrates multiple “agents” (Outline, Background, Persona, Plot, Feedback, Revision, Synthesis, Verification), each backed by a shared LLM client, to produce and refine narrative drafts.

---

##  Features

- **Modular Agents**  
  - Outline → Background → Persona → Plot → Feedback → Revision → Synthesis → Verification  
  - Each agent in its own package, with separate prompt templates (YAML).

- **Human-in-the-Loop**  
  - Inspect & edit after every LLM step via `prompt_edit()`.
  - Collect both LLM and human feedback before revision.

- **Configurable Generation**  
  - Centralized settings in `configs/api_config.yml` (model, endpoint, timeouts, sampling).
  - `.env` support via `python-dotenv`.

- **Streaming & Batch Modes**  
  - Support for streaming or blocking LLM responses.
  - Automatic handling of JSON and NDJSON formats.

- **Testing & CI**  
  - Unit tests for every agent and client in `tests/`.
  - Example GitHub Actions workflow for automated linting & `pytest`.

---

##  Folder Structure

```

agentic\_story/
├── configs/           # YAML configs (api, logging, generation defaults)
├── prompts/           # LLM “system” & “user” templates (one YAML per agent)
├── modules/
│   ├── clients/       # LLMClient implementation
│   ├── agents/        # Agents: outline, plot, feedback, revision, …
│   ├── pipeline/      # `run_pipeline.py` orchestrator
│   └── utils/         # Shared helpers (I/O, logging, parsing)
├── scripts/           # Convenience scripts (start\_local.sh, deploy.sh)
├── data/              # Examples & output
├── tests/             # Unit & integration tests
├── .env               # Local environment variables (not checked in)
├── requirements.txt   # Python dependencies
└── README.md          # This file

````

---

##  Installation

1. **Clone the repo**  
   ```bash
   git clone https://github.com/your-org/agentic_story.git
   cd agentic_story
````

2. **Create & activate a virtual environment**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---
Image
!(Agentic Story Diagram-Page-7.drawio.png)


---

## 📝 Configuration

1. **Copy `.env.example` to `.env`** (create if missing):

   ```dotenv
   # .env
   LLM_API_URL=https://llm.srv.webis.de/api/chat
   LLM_MODEL=default
   API_CONFIG_PATH=agentic_story/configs/api_config.yml
   ```

2. **Edit `configs/api_config.yml`** to tweak:

   * `llm_api.url` / `model` / `timeout` / `stream`
   * `generation.max_tokens` / `temperature` / `top_p` / `frequency_penalty` / `presence_penalty`

3. **(Optional) Logging**

   * Configure `configs/logging.yml` to adjust log levels, handlers, and formatters.

---

## ▶ Usage

Run the full interactive pipeline:

```bash
# via start_local.sh (exports env & starts pipeline)
./scripts/start_local.sh

# or manually:
python3 modules/pipeline/run_pipeline.py
```

1. Enter your story idea.
2. Review & optionally edit each LLM-generated step: outline, draft, feedback.
3. Provide free-form human feedback.
4. Receive the final revised story.

---

##  Testing & CI  (TODO)

* **Run tests locally**

  ```bash
  pytest --maxfail=1 --disable-warnings -q
  ```

* **GitHub Actions**
  A workflow at `.github/workflows/ci.yml` installs dependencies and runs your test suite on every push & PR to `main`.

---

##  Contributing

1. Fork the repo & create a feature branch.
2. Add or update tests in `tests/`.
3. Submit a PR with a clear description of your changes.



```
![image](https://github.com/user-attachments/assets/8d5e0c61-dae6-40f9-9ae2-aa4e52a55807)
Save this as **`README.md`** at your project root. Feel free to adjust URLs, badge images, or any section to match your organization’s conventions.
```
