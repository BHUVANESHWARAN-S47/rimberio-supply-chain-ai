import os
import chromadb
from chromadb.config import Settings as ChromaSettings
from backend.app.core.config import settings

def get_chroma_client():
    """Initializes and returns a ChromaDB client.
    Connects via HttpClient if host is specified, otherwise initializes persistent local client.
    """
    chroma_host = os.getenv("CHROMA_HOST")
    chroma_port = int(os.getenv("CHROMA_PORT", 8000))
    persist_dir = os.getenv("CHROMA_PERSIST_DIRECTORY", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "chroma_db")))

    if chroma_host and chroma_host not in ["localhost", "127.0.0.1"]:
        try:
            return chromadb.HttpClient(host=chroma_host, port=chroma_port)
        except Exception as e:
            print(f"[ChromaDB] Could not connect to remote host {chroma_host}:{chroma_port}: {e}. Falling back to persistent client.")

    os.makedirs(persist_dir, exist_ok=True)
    return chromadb.PersistentClient(path=persist_dir)

def check_chroma_connection() -> dict:
    """Health check verifying vector database connectivity."""
    try:
        client = get_chroma_client()
        collections = client.list_collections()
        col_names = [c.name for c in collections]
        return {
            "status": "CONNECTED",
            "is_healthy": True,
            "collections_count": len(col_names),
            "collections": col_names
        }
    except Exception as e:
        return {
            "status": "DISCONNECTED",
            "is_healthy": False,
            "error": str(e)
        }
