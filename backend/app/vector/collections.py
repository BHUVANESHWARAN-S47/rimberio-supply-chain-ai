from typing import Dict, Any
from backend.app.vector.client import get_chroma_client

COLLECTION_NAMES = [
    "rimberio_supplier_memory",
    "rimberio_negotiation_memory",
    "rimberio_decision_memory",
    "rimberio_risk_memory",
    "rimberio_document_memory",
    "rimberio_simulation_memory"
]

def init_chroma_collections():
    """Ensures all 6 designated semantic collections are initialized in ChromaDB."""
    client = get_chroma_client()
    collections = {}
    for name in COLLECTION_NAMES:
        col = client.get_or_create_collection(
            name=name,
            metadata={"description": f"Semantic agentic memory store for {name}"}
        )
        collections[name] = col
    return collections

def get_collection(collection_name: str):
    """Retrieves a specific ChromaDB collection."""
    if collection_name not in COLLECTION_NAMES:
        raise ValueError(f"Collection {collection_name} is not one of designated RIMBERIO collections.")
    client = get_chroma_client()
    return client.get_or_create_collection(name=collection_name)
