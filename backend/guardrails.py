"""SQL safety guardrails.

IntelliQuery only ever runs read-only SELECTs. We reject anything that could
modify data or run multiple statements. This is what makes it safe to expose to
non-technical users.
"""
import re

BLOCKED = ["insert", "update", "delete", "drop", "alter", "create",
           "truncate", "replace", "attach", "pragma", "grant", "revoke"]

class UnsafeSQLError(Exception):
    pass

def validate_sql(sql: str) -> str:
    s = sql.strip().rstrip(";").strip()
    if not s:
        raise UnsafeSQLError("Empty query.")
    if ";" in s:
        raise UnsafeSQLError("Multiple statements are not allowed.")
    low = s.lower()
    if not low.startswith("select") and not low.startswith("with"):
        raise UnsafeSQLError("Only SELECT queries are allowed.")
    for word in BLOCKED:
        if re.search(rf"\b{word}\b", low):
            raise UnsafeSQLError(f"Blocked keyword detected: {word}")
    return s
