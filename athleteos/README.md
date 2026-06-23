# AthleteOS

AthleteOS is a production-style **multi-agent health coaching system** built with LangGraph.
An Orchestrator coordinates four specialist agents:

- Nutrition Agent
- Workout Agent
- Recovery Agent
- Progress Agent

The key feature is explicit **inter-agent conflict detection + conflict resolution**.
If recovery risk contradicts workout intensity, the orchestrator overrides the workout and explains why.

## Architecture

1. User inputs are collected in Streamlit (`app.py`)
2. LangGraph executes sub-agents in sequence:
   - nutrition -> workout -> recovery -> progress
3. Orchestrator reads all outputs, detects conflicts, resolves them, and assembles final unified plan
4. UI displays:
   - Final plan
   - Conflicts detected
   - Conflicts resolved
   - Raw outputs from each sub-agent

## Run Locally

1. Create a virtualenv and install dependencies:

```bash
pip install -r requirements.txt
```

2. Add a `.env` file:

```bash
GROQ_API_KEY=your_groq_key
TAVILY_API_KEY=your_tavily_key
```

3. Launch:

```bash
streamlit run app.py
```

## Conflict Resolution Example

- Workout Agent: heavy lower-body training
- Recovery Agent: high fatigue due to low sleep + leg soreness
- Orchestrator:
  - Detects incompatibility
  - Replaces session with recovery-compatible upper-body session
  - Logs explanation in `orchestrator_notes`

This explicit override logic is implemented in `agents/orchestrator.py`.
