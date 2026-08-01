"""Semantic layer + lightweight retrieval (the 'RAG' in IntelliQuery).

Each table has a plain-English description and column notes. Given a user
question, we retrieve the most relevant table descriptions by keyword overlap
and feed only those into the LLM prompt. This keeps prompts small, grounds the
model in real business definitions, and improves SQL accuracy.
"""
import re

TABLES = {
    "customers": {
        "desc": "One row per customer. Use for anything about customers, sign-ups, countries.",
        "columns": "customer_id, name, country, signup_date",
        "keywords": ["customer", "customers", "country", "signup", "sign up", "user", "buyer", "who"],
    },
    "products": {
        "desc": "One row per product with its category and price.",
        "columns": "product_id, name, category, price",
        "keywords": ["product", "products", "category", "price", "item", "catalog", "expensive", "cheap"],
    },
    "orders": {
        "desc": "One row per order, linked to a customer. status is completed/cancelled.",
        "columns": "order_id, customer_id, order_date, status",
        "keywords": ["order", "orders", "purchase", "status", "completed", "cancelled", "date", "month"],
    },
    "order_items": {
        "desc": "Line items for each order (which product, how many). Join to orders and products.",
        "columns": "order_item_id, order_id, product_id, quantity",
        "keywords": ["item", "items", "quantity", "sold", "units", "line", "how many", "revenue", "sales"],
    },
}

def retrieve_context(question: str, top_k: int = 4) -> str:
    q = question.lower()
    scored = []
    for name, meta in TABLES.items():
        score = sum(1 for kw in meta["keywords"] if kw in q)
        scored.append((score, name, meta))
    scored.sort(key=lambda x: x[0], reverse=True)
    # always include at least the top table; include others that scored > 0
    chosen = [s for s in scored if s[0] > 0][:top_k] or scored[:2]
    lines = []
    for _, name, meta in chosen:
        lines.append(f"TABLE {name} ({meta['columns']}) -- {meta['desc']}")
    return "\n".join(lines)

def full_schema() -> str:
    return "\n".join(
        f"TABLE {n} ({m['columns']}) -- {m['desc']}" for n, m in TABLES.items()
    )
