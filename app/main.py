import json
import uuid
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.intent import needs_currency, needs_rag, needs_weather, parse_currency_request, parse_days
from app.llm import generate_answer
from app.mcp_client import convert_currency, get_weather
from app.memory import memory_text, update_memory
from app.rag import retrieve_context

BASE_DIR = Path(__file__).resolve().parents[1]

app = FastAPI(title="AI Travel Planning Assistant")
app.mount("/static", StaticFiles(directory=BASE_DIR / "app" / "static"), name="static")


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=2)
    session_id: str | None = None


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    sources: list[dict]
    tool_results: list[dict]
    mode: str


@app.get("/", response_class=HTMLResponse)
def index():
    return (BASE_DIR / "app" / "static" / "index.html").read_text(encoding="utf-8")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())
    update_memory(session_id, request.message)

    context = ""
    sources: list[dict] = []
    tool_results: list[dict] = []
    modes = []

    if needs_rag(request.message):
        context, sources = retrieve_context(request.message)
        modes.append("RAG")

    if needs_weather(request.message):
        try:
            weather = await get_weather("Singapore", parse_days(request.message))
            tool_results.append({"tool": "MCP weather", "result": weather})
        except Exception as exc:
            tool_results.append({"tool": "MCP weather", "error": str(exc)})
        modes.append("MCP Weather")

    if needs_currency(request.message):
        parsed = parse_currency_request(request.message)
        if parsed:
            amount, source, target = parsed
            try:
                currency = await convert_currency(amount, source, target)
                tool_results.append({"tool": "MCP currency", "result": currency})
            except Exception as exc:
                tool_results.append({"tool": "MCP currency", "error": str(exc)})
        else:
            tool_results.append({"tool": "MCP currency", "error": "Currency request was detected, but amount or currencies were not clear."})
        modes.append("MCP Currency")

    if not context and not tool_results:
        context, sources = retrieve_context(request.message)
        modes.append("RAG")

    answer = generate_answer(
        question=request.message,
        memory=memory_text(session_id),
        context=context,
        tool_results=json.dumps(tool_results, indent=2, ensure_ascii=False),
        sources=sources,
    )

    return ChatResponse(
        session_id=session_id,
        answer=answer,
        sources=sources,
        tool_results=tool_results,
        mode=" + ".join(dict.fromkeys(modes)),
    )
