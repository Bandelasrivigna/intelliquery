# IntelliQuery — Natural-Language-to-SQL Data Assistant

Ask questions about your data in plain English. IntelliQuery retrieves the
relevant schema, uses an LLM to generate a **safe, read-only SQL query**,
validates it, runs it against a sample analytics warehouse, and returns the
results — so non-technical users can self-serve reliable answers without
waiting on the data team.

> Built with Python, FastAPI, an LLM (Anthropic Claude or OpenAI), a retrieval
> (RAG) layer over a semantic schema, and SQL safety guardrails.

---

## Why it exists
Data teams get flooded with ad-hoc "can you pull X?" requests. IntelliQuery
turns those into self-serve answers, while staying safe (read-only only) and
grounded (the model only sees the real schema and business definitions).

## How it works
```
question ─► retrieve schema context (RAG) ─► LLM generates SQL
                                                   │
                                     guardrails: read-only, single SELECT
                                                   │
                                     execute on warehouse ─► results + SQL
```

1. **Schema retrieval (RAG).** `schema_context.py` holds a plain-English
   description of every table/column. For each question it retrieves only the
   relevant tables, keeping the prompt small and grounding the model in real
   business definitions.
2. **LLM generation.** `nl2sql.py` builds a tightly-scoped prompt and asks
   Claude/OpenAI for a single SELECT. Pluggable via env vars.
3. **Guardrails.** `guardrails.py` rejects anything that isn't a single
   read-only SELECT (no INSERT/UPDATE/DELETE/DROP, no multiple statements).
4. **Execution.** Runs against a local SQLite warehouse (`database.py`) seeded
   with an e-commerce dataset (customers, products, orders, order_items).

## Tech stack
Python · FastAPI · SQLite · Anthropic Claude / OpenAI · RAG · Prompt engineering

## Quickstart
```bash
pip install -r requirements.txt
uvicorn backend.app:app --reload
# open http://127.0.0.1:8000
```
Runs **out of the box in demo mode** (no API key needed) for the example
questions. For full natural-language querying, set an API key:
```bash
export ANTHROPIC_API_KEY=sk-...   # or OPENAI_API_KEY=sk-...
```

## Example questions
- "What is the revenue by product?"
- "Which is the top selling product?"
- "List customers in the USA"
- "How many completed orders are there?"
- "How many orders does each customer have?"

## Project structure
```
IntelliQuery/
├── backend/
│   ├── app.py            # FastAPI app + routes
│   ├── nl2sql.py         # NL→SQL engine (LLM + retrieval + fallback)
│   ├── schema_context.py # semantic layer + RAG retrieval
│   ├── guardrails.py     # SQL safety validation
│   └── database.py       # sample warehouse + seed data
├── frontend/
│   └── index.html        # simple web UI
├── requirements.txt
└── README.md
```

## Safety & design notes
- **Read-only by design** — guardrails block all data-modifying statements.
- **Grounded** — the model only sees the schema, reducing hallucinated tables/columns.
- **Provider-agnostic** — works with Claude or OpenAI; demo fallback needs no key.

## Future work
- Add query cost/row-limit guards, caching, and a feedback loop to improve prompts.
- Support a real warehouse (Snowflake/BigQuery) via a connection string.
- Add unit tests and CI.

---
Built by **Srivigna Reddy Bandela** · [LinkedIn](https://www.linkedin.com/in/srivigna-reddy-bandela-379b51229/)
