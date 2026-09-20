import os

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.prompts import ANSWER_PROMPT, SYSTEM_PROMPT

load_dotenv()


def _gemini_chain():
    from langchain_google_genai import ChatGoogleGenerativeAI

    model = ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
        temperature=0.2,
    )
    prompt = ChatPromptTemplate.from_messages(
        [("system", SYSTEM_PROMPT), ("human", ANSWER_PROMPT)]
    )
    return prompt | model | StrOutputParser()


def fallback_answer(question: str, context: str, tool_results: str, sources: list[dict]) -> str:
    source_lines = "\n".join(f"- {s['title']}: {s['url']}" for s in sources) or "- No source retrieved"
    context_preview = context[:1600].strip()
    tool_section = tool_results if tool_results else "No current MCP tool information was required."
    return (
        "## Answer\n"
        "I found relevant Singapore travel knowledge from the local knowledge base. "
        "The key planning guidance is below.\n\n"
        f"{context_preview}\n\n"
        "## Current information used\n"
        f"{tool_section}\n\n"
        "## Recommendation\n"
        "Use the retrieved destination guidance as stable travel knowledge. Where weather or currency information is shown, treat it as current MCP-provided information. "
        "For itinerary questions, group nearby attractions together and keep indoor alternatives for rainy or very hot periods.\n\n"
        "## Sources used\n"
        f"{source_lines}"
    )


def generate_answer(question: str, memory: str, context: str, tool_results: str, sources: list[dict]) -> str:
    if not os.getenv("GOOGLE_API_KEY"):
        return fallback_answer(question, context, tool_results, sources)
    try:
        chain = _gemini_chain()
        return chain.invoke(
            {
                "question": question,
                "memory": memory,
                "context": context,
                "tool_results": tool_results or "No MCP tool was required.",
            }
        )
    except Exception as exc:
        return fallback_answer(question, context, f"MCP/LLM fallback note: {exc}\n{tool_results}", sources)
