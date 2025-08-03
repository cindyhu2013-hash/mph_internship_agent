# MPH Internship Hunter Agent

This repository is a minimal starter kit for an AI agent that finds Summer 2026 MPH‑level internships every day, scores them, and writes the results to your Google Sheet.

## Quick start (once Python and Git are installed)

1. Open a terminal in this folder.
2. Create a virtual environment:

```
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

3. Install dependencies:

```
pip install -r requirements.txt
```

4. Add secrets:

Create a file called `.env` at project root:

```
SHEET_ENDPOINT=https://script.google.com/macros/s/XXXXXXXX/exec
SERP_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxx
SLACK_WEBHOOK=
```

5. Run the agent:

```
python agent.py
```

6. Commit and push to GitHub when you are ready, then enable the GitHub Actions workflow in `.github/workflows/agent.yml`.

See `config/rules.yaml` to tune keywords, states, score weights, and `config/targets.yaml` to seed employer career pages.
