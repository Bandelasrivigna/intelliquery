"""IntelliQuery API — FastAPI backend."""
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
import database, nl2sql

app = FastAPI(title="IntelliQuery", description="Natural-Language-to-SQL data assistant")

@app.on_event("startup")
def _startup():
    database.init_db()

class Ask(BaseModel):
    question: str

@app.post("/api/query")
def query(body: Ask):
    return nl2sql.answer(body.question)

@app.get("/api/schema")
def schema():
    from schema_context import full_schema
    return {"schema": full_schema()}

FRONTEND = Path(__file__).parent.parent / "frontend"

@app.get("/")
def index():
    return FileResponse(FRONTEND / "index.html")

# uvicorn backend.app:app --reload   (run from project root)
