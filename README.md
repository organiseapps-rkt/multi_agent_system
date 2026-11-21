# Multi-Agent Travel Assistant

A local command-line travel assistant built with LangGraph. It searches for flight information and hotels, generates an itinerary with Groq, and stores graph checkpoints in PostgreSQL.

## Requirements

- Python 3.10 or newer
- A PostgreSQL database that the application can connect to
- API credentials for Groq, Tavily, and Aviationstack

## Setup

From the project directory, create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

If you already have the project's `langgraph_env1` environment, activate it with `source langgraph_env1/bin/activate` instead.

Install the Python dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Create a `.env` file in the project root and set the required values:

```dotenv
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
AVIATION_API_KEY=your_aviationstack_api_key
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
```

The application defaults to the Groq model `openai/gpt-oss-120b`. To use another model available to your Groq account, optionally add:

```dotenv
GROQ_MODEL=your_available_groq_model_id
```

Ensure the PostgreSQL server is running and the database named in `DATABASE_URL` already exists. On startup, LangGraph initializes its checkpoint schema in that database. Keep `.env` private and do not commit API keys or database credentials.

## Run

With the virtual environment activated, run:

```bash
python main.py
```

Enter a travel request when prompted. The workflow calls the external flight, hotel-search, and language-model APIs, so valid credentials and network access are required.

To leave the virtual environment:

```bash
deactivate
```