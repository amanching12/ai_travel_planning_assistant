from app.rag import build_vector_store

if __name__ == "__main__":
    store = build_vector_store()
    print(f"Knowledge base indexed. Chunks stored: {store._collection.count()}")
