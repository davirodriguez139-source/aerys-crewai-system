# AERYS CrewAI System

Production-ready multi-agent CrewAI workflow for generating **USA-market campaign assets** for AERYS Sleep Strips.

The system implements 4 agents based on your AERYS operating docs:
- **Director Agent** (orchestration + final quality review)
- **Research Agent** (market, competitor, trend intelligence)
- **Copy Agent** (conversion-focused messaging and offers)
- **Ads Agent** (hooks, scripts, and platform-ready ad concepts)

---

### Project Structure

```text
aerys_crewai_system/
├── main.py
├── requirements.txt
├── .env.example
├── README.md
├── config/
├── outputs/
└── src/
    ├── __init__.py
    ├── agents.py
    ├── tasks.py
    └── crew.py
```

---

### Requirements

- Python 3.10+
- Anthropic API key (Claude)

---

### Installation

```bash
cd /home/ubuntu/aerys_crewai_system
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

### Environment Setup

```bash
cp .env.example .env
```

Edit `.env` and set at least:

```env
ANTHROPIC_API_KEY=your_real_key_here
```

Optional for future research tool activation:

```env
SERPER_API_KEY=your_serper_key_here
```

> If `SERPER_API_KEY` is configured, the Research Agent is automatically prepared to use a web search tool.

---

### Usage

Run:

```bash
python main.py
```

Then enter a campaign goal, for example:

- `Create ad for jawline angle`
- `Promote better deep sleep for high-performance professionals`
- `Build offer-centered campaign for first-time buyers`

The workflow runs sequentially:

1. Research Agent → Market intelligence brief
2. Copy Agent → Conversion copy package
3. Ads Agent → Scripts + creative concepts
4. Director Agent → Final strategic review and approval

Final output is saved as:

```text
outputs/YYYY-MM-DD_campaign-name.md
```

---

### Agent & Task Design

- **English-only deliverables** for the USA market.
- **Non-generic requirement** enforced in prompts.
- **Premium biohacking positioning** for AERYS Sleep Strips.
- **Direct-response orientation** with conversion and profit focus.

---

### Troubleshooting

- **Error: `ANTHROPIC_API_KEY is missing`**
  - Ensure `.env` exists and contains a valid key.
- **Import errors**
  - Activate virtual environment and reinstall dependencies.
- **No web-search tool attached to research agent**
  - Add `SERPER_API_KEY` in `.env`.

---

### Notes

- Outputs are generated from the AERYS strategic framework extracted from your uploaded markdown system.
- `outputs/` is execution-ready and can be connected to your internal delivery protocol.
