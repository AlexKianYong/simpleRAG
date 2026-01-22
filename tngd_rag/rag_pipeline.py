"""
RAG Pipeline module for document retrieval and generation.
Handles:
- Document chunking
- Embedding generation
- Vector retrieval
- LLM generation using Ollama
"""

import json
import os
from typing import List, Dict, Any
import chromadb


class DocumentChunker:
    """Handles document chunking with overlap."""
    
    def __init__(self, chunk_size: int = 300, overlap: int = 50):
        """
        Initialize chunker.
        
        Args:
            chunk_size: Size of each chunk in characters
            overlap: Overlap between chunks in characters
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_document(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Split document into overlapping chunks.
        
        Args:
            text: Document text to chunk
            metadata: Metadata to attach to chunks
            
        Returns:
            List of chunk dictionaries
        """
        chunks = []
        words = text.split()
        current_chunk = []
        
        for word in words:
            current_chunk.append(word)
            chunk_text = ' '.join(current_chunk)
            
            if len(chunk_text) >= self.chunk_size:
                chunks.append({
                    'text': chunk_text,
                    'metadata': metadata.copy() # url and category
                })
                
                # Keep last overlap words for next chunk
                overlap_words = int(self.overlap / 5) 
                # approximately 50 words around 5 words
                current_chunk = current_chunk[-overlap_words:] if overlap_words > 0 else []
        
        # Add remaining text
        if current_chunk:
            chunks.append({
                'text': ' '.join(current_chunk),
                'metadata': metadata.copy()
            })
        
        return chunks


class ChromaDBStore:
    """Manages ChromaDB vector store."""
    
    def __init__(self, persist_dir: str = "./chromadb_store"):
        """
        Initialize ChromaDB store.
        
        Args:
            persist_dir: Directory to persist ChromaDB
        """
        os.makedirs(persist_dir, exist_ok=True)
        
        # Use new ChromaDB API (0.5.3+)
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = None
        self.persist_dir = persist_dir
    
    def create_collection(self, collection_name: str = "tngd_faq"):
        """Create or get a collection."""
        # Delete existing collection if it exists
        try:
            self.client.delete_collection(collection_name)
        except:
            pass
        
        self.collection = self.client.create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        return self.collection
    
    def add_documents(self, documents: List[Dict[str, str]]):
        """
        Add documents to collection.
        
        Args:
            documents: List of documents with 'id', 'text', and 'metadata'
        """
        if not self.collection:
            raise ValueError("Collection not initialized. Call create_collection first.")
        
        ids = [doc['id'] for doc in documents]
        texts = [doc['text'] for doc in documents]
        metadatas = [doc.get('metadata', {}) for doc in documents]
        
        self.collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas
        )
    
    def query(self, query_text: str, n_results: int = 5) -> Dict[str, Any]:
        """
        Query the collection.
        
        Args:
            query_text: Query text
            n_results: Number of results to return
            
        Returns:
            Query results
        """
        if not self.collection:
            raise ValueError("Collection not initialized. Call create_collection first.")
        
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results
    
    def persist(self):
        """Persist the collection to disk (automatic in new API)."""
        # ChromaDB 0.5.3+ auto-persists, so this is now optional
        pass


class OllamaLLM:
    """Interface for Ollama LLM."""
    
    def __init__(self, model_name: str = "mistral", base_url: str = "http://localhost:11434"):
        """
        Initialize Ollama LLM.
        
        Args:
            model_name: Name of the Ollama model
            base_url: Base URL for Ollama API
        """
        self.model_name = model_name
        self.base_url = base_url
        
        # Import here to avoid hard dependency
        try:
            import ollama
            self.ollama = ollama
        except ImportError:
            raise ImportError("Ollama not installed. Run: pip install ollama")
    
    def generate(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Generate text using Ollama.
        
        Args:
            prompt: Input prompt
            temperature: Temperature for generation
            
        Returns:
            Generated text
        """
        try:
            response = self.ollama.generate(
                model=self.model_name,
                prompt=prompt,
                stream=False,
                options={
                    'temperature': temperature
                }
            )
            return response.get('response', '').strip()
        except Exception as e:
            raise RuntimeError(f"Error generating text with Ollama: {e}")


class RAGPipeline:
    """Main RAG Pipeline orchestrator."""
    
    def __init__(self, 
                 chromadb_dir: str = "./chromadb_store",
                 model_name: str = "mistral",
                 chunk_size: int = 300,
                 retrieval_top_k: int = 5):
        """
        Initialize RAG pipeline.
        
        Args:
            chromadb_dir: Directory for ChromaDB persistence
            model_name: Ollama model name
            chunk_size: Size of text chunks
            retrieval_top_k: Number of top chunks to retrieve
        """
        self.chromadb = ChromaDBStore(chromadb_dir)
        self.llm = OllamaLLM(model_name)
        self.chunker = DocumentChunker(chunk_size=chunk_size)
        self.retrieval_top_k = retrieval_top_k
    
    def add_knowledge_base(self, documents: List[Dict[str, Any]]):
        """
        Add documents to knowledge base.
        
        Args:
            documents: List of documents with 'question', 'answer', 'url', etc.
        """
        self.chromadb.create_collection()
        
        processed_docs = []
        doc_id = 0
        
        for doc in documents:
            # Chunk the answer
            answer_chunks = self.chunker.chunk_document(
                doc.get('answer', ''),
                {
                    'source': 'question_answer',
                    'question': doc.get('question', ''),
                    'url': doc.get('url', ''),
                    'category': doc.get('category', 'general'),
                    'full_answer': doc.get('answer', '')[:800]  # Preview
                }
            )
            
            for chunk in answer_chunks:
                processed_docs.append({
                    'id': f"doc_{doc_id}",
                    'text': chunk['text'],
                    'metadata': chunk['metadata']
                })
                doc_id += 1
        
        self.chromadb.add_documents(processed_docs)
        self.chromadb.persist()
    
    def retrieve(self, query: str) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks for a query.
        
        Args:
            query: User query
            
        Returns:
            List of retrieved chunks
        """
        results = self.chromadb.query(query, n_results=self.retrieval_top_k)
        
        chunks = []
        if results['documents'] and len(results['documents']) > 0:
            for i, doc in enumerate(results['documents'][0]):
                chunks.append({
                    'text': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results['distances'] else 0
                })
        
        return chunks
    
    def generate_answer(self, question: str, retrieved_chunks: List[Dict[str, Any]]) -> str:
        context_items = []
        url = "-"
        for i, chunk in enumerate(retrieved_chunks):
            text = chunk['text']
            if url == "-" :
                url = chunk['metadata'].get('url', '-')
            context_items.append(f"Context {i+1} :{text}")
        
        context = "\n\n".join(context_items)
        
        prompt = f"""You are a helpful assistant for Touch 'n Go (TNG) eWallet FAQ.
                Answer the following question based ONLY on the provided context.
                If the information is not in the context, say "I don't have information about that in the FAQ."

                Context:
                {context}

                Question: {question}

                Answer:

                """
                    
        answer = self.llm.generate(prompt, temperature=0.5)
        return answer, url
    
    def process_question(self, question: str) -> Dict[str, Any]:
        """
        Process a question through the full RAG pipeline.
        
        Args:
            question: User question
            
        Returns:
            Dictionary with retrieved chunks and generated answer
        """
        retrieved_chunks = self.retrieve(question)
        answer, url = self.generate_answer(question, retrieved_chunks)
        
        return {
            'retrieved_chunks': retrieved_chunks,
            'answer': answer + "\n\nReferencee URL - " + url
        }
