# rc-raux-bot
A chatbot handling RAUX ticket intake.


## Installation

0. [Install `uv`](https://docs.astral.sh/uv/getting-started/installation/)

1. Clone the repository `git clone git@github.com:dartmouth/rc-raux-bot.git`

2. In the repo root, initialize environment: `uv sync`

## Getting Started

1. Run the backend API server:

```
uv run uvicorn src.chatbot.api.main:app --reload --host 0.0.0.0 --port 8000
```

2. Start the frontend server:

```
uv run chainlit run frontend/app.py --host 0.0.0.0 --port 8001
```

