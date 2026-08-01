"""Natural-Language-to-SQL engine.

Pipeline:
  1. Retrieve relevant schema/semantic context for the question (schema_context).
  2. Build a tightly-scoped prompt and ask an LLM to produce a single SELECT.
  3. Validate the SQL with guardrails (read-only, single statement).
  4. Execute against the sample warehouse and return rows + the SQL + an explanation.

LLM providers are pluggable via environment variables:
  - ANTHROPIC_API_KEY  -> uses Claude
  - OPENAI_API_KEY     -> uses OpenAI
If neither is set, a small demo fallback handles the example questions so the
app runs out of the box.
"""
import os, re
from schema_context import retrieve_context
from guardrails import validate_sql, UnsafeSQLError

PROMPT = """You are IntelliQuery, a careful data analyst that writes SQLite SQL.
Use ONLY the tables and columns below. Return a SINGLE read-only SELECT query and nothing else.
Never write INSERT/UPDATE/DELETE/DROP. Do not add explanations or markdown fences.

Relevant schema:
{context}

Question: {question}
SQL:"""

def _clean(sql: str) -> str:
    sql = re.sub(r"```sql|```", "", sql, flags=re.I).strip()
    return sql

def _llm_sql(question: str, context: str) -> str:
    prompt = PROMPT.format(context=context, question=question)
    if os.getenv("ANTHROPIC_API_KEY"):
        import anthropic
        client = anthropic.Anthropic()
        msg = client.messages.create(
            model="claude-3-5-sonnet-latest", max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        return _clean(msg.content[0].text)
    if os.getenv("OPENAI_API_KEY"):
        from openai import OpenAI
        client = OpenAI()
        resp = client.chat.completions.create(
            model="gpt-4o-mini", max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        return _clean(resp.choices[0].message.content)
    raise RuntimeError("NO_LLM")

# --- demo fallback so the project runs with zero API keys ---
_DEMO = {
    "revenue": "SELECT p.name, SUM(oi.quantity*p.price) AS revenue FROM order_items oi JOIN products p ON oi.product_id=p.product_id GROUP BY p.name ORDER BY revenue DESC",
    "top product": "SELECT p.name, SUM(oi.quantity) AS units_sold FROM order_items oi JOIN products p ON oi.product_id=p.product_id GROUP BY p.name ORDER BY units_sold DESC LIMIT 1",
    "customers usa": "SELECT name, country FROM customers WHERE country='USA'",
    "completed orders": "SELECT COUNT(*) AS completed_orders FROM orders WHERE status='completed'",
    "orders per customer": "SELECT c.name, COUNT(o.order_id) AS orders FROM customers c LEFT JOIN orders o ON c.customer_id=o.customer_id GROUP BY c.name ORDER BY orders DESC",
}
def _demo_sql(question: str) -> str:
    q = question.lower()
    if "revenue" in q or "sales" in q: return _DEMO["revenue"]
    if "top" in q and ("product" in q or "sell" in q): return _DEMO["top product"]
    if ("usa" in q or "united states" in q) and "customer" in q: return _DEMO["customers usa"]
    if "completed" in q and "order" in q: return _DEMO["completed orders"]
    if "order" in q and "customer" in q: return _DEMO["orders per customer"]
    return _DEMO["orders per customer"]

def answer(question: str) -> dict:
    context = retrieve_context(question)
    used_llm = True
    try:
        sql = _llm_sql(question, context)
    except RuntimeError:
        used_llm = False
        sql = _demo_sql(question)
    try:
        safe_sql = validate_sql(sql)
    except UnsafeSQLError as e:
        return {"error": f"Query rejected by guardrails: {e}", "sql": sql}
    from database import run_query
    try:
        cols, rows = run_query(safe_sql)
    except Exception as e:
        return {"error": f"Execution error: {e}", "sql": safe_sql}
    return {
        "sql": safe_sql,
        "columns": cols,
        "rows": rows,
        "mode": "llm" if used_llm else "demo",
        "context_used": context,
    }
