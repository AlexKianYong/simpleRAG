"""
TNGD RAG System Package
Retrieval-Augmented Generation for Touch 'n Go FAQ
"""

__version__ = "1.0.0"
__description__ = "RAG System for TNGD FAQ powered by Ollama and ChromaDB"

from .bot import ask_tngd_bot, initialize_bot, load_knowledge_base
from .guardrails import AdversarialGuardrails
from .rag_pipeline import RAGPipeline, ChromaDBStore, OllamaLLM, DocumentChunker

__all__ = [
    'ask_tngd_bot',
    'initialize_bot',
    'load_knowledge_base',
    'AdversarialGuardrails',
    'RAGPipeline',
    'ChromaDBStore',
    'OllamaLLM',
    'DocumentChunker',
]
