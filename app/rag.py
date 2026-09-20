from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

BASE_DIR = Path(__file__).resolve().parents[1]
KB_DIR = BASE_DIR / "knowledge_base"
VECTOR_DIR = BASE_DIR / "vector_store"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def _parse_markdown(path: Path) -> Document:
    text = path.read_text(encoding="utf-8")
    metadata = {"source_file": path.name}
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            frontmatter, body = parts[1], parts[2].strip()
            for line in frontmatter.splitlines():
                if ":" in line:
                    key, value = line.split(":", 1)
                    metadata[key.strip()] = value.strip()
            text = body
    metadata.setdefault("title", path.stem.replace("_", " ").title())
    metadata.setdefault("source_url", "")
    return Document(page_content=text, metadata=metadata)


def load_documents() -> list[Document]:
    docs = []
    for path in sorted(KB_DIR.glob("*.md")):
        docs.append(_parse_markdown(path))
    return docs


def embedding_function():
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


def build_vector_store() -> Chroma:
    splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=120)
    chunks = splitter.split_documents(load_documents())
    return Chroma.from_documents(
        documents=chunks,
        embedding=embedding_function(),
        persist_directory=str(VECTOR_DIR),
        collection_name="singapore_travel_kb",
    )


def get_vector_store() -> Chroma:
    VECTOR_DIR.mkdir(parents=True, exist_ok=True)
    store = Chroma(
        persist_directory=str(VECTOR_DIR),
        embedding_function=embedding_function(),
        collection_name="singapore_travel_kb",
    )
    try:
        if store._collection.count() == 0:
            store = build_vector_store()
    except Exception:
        store = build_vector_store()
    return store


def retrieve_context(question: str, k: int = 5) -> tuple[str, list[dict]]:
    store = get_vector_store()
    docs = store.similarity_search(question, k=k)
    context_blocks = []
    sources = []
    seen = set()
    for i, doc in enumerate(docs, start=1):
        title = doc.metadata.get("title", "Knowledge Base")
        url = doc.metadata.get("source_url", "")
        context_blocks.append(f"[Source {i}: {title}]\n{doc.page_content}")
        key = (title, url)
        if key not in seen:
            seen.add(key)
            sources.append({"title": title, "url": url})
    return "\n\n".join(context_blocks), sources
