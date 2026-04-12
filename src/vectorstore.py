import os
import chromadb
import numpy as np
from typing import List, Any
from sentence_transformers import SentenceTransformer
from src.embedding import EmbeddingPipeline


class ChromaVectorStore:
    def __init__(
        self,
        persist_dir: str = "chroma_store",
        embedding_model: str = "all-MiniLM-L6-v2",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        self.persist_dir = persist_dir
        os.makedirs(self.persist_dir, exist_ok=True)
        self.embedding_model = embedding_model
        self.model = SentenceTransformer(embedding_model)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Initialize ChromaDB persistent client
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.collection = self.client.get_or_create_collection(name="documents")
        print(f"[INFO] Loaded embedding model: {embedding_model}")
        print(f"[INFO] ChromaDB initialized at: {self.persist_dir}")

    def build_from_documents(self, documents: List[Any]):
        print(f"[INFO] Building vector store from {len(documents)} raw documents...")
        emb_pipe = EmbeddingPipeline(
            model_name=self.embedding_model,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )
        chunks = emb_pipe.chunk_documents(documents)
        embeddings = emb_pipe.embed_chunks(chunks)
        metadatas = [{"text": chunk.page_content} for chunk in chunks]
        self.add_embeddings(np.array(embeddings).astype("float32"), metadatas)
        print(f"[INFO] Vector store built and saved to {self.persist_dir}")

    def add_embeddings(self, embeddings: np.ndarray, metadatas: List[Any] = None):
        count = self.collection.count()
        ids = [str(i + count) for i in range(len(embeddings))]
        documents = (
            [m.get("text", "") for m in metadatas]
            if metadatas
            else [""] * len(embeddings)
        )
        self.collection.add(
            ids=ids,
            embeddings=embeddings.tolist(),
            metadatas=metadatas,
            documents=documents,
        )
        print(f"[INFO] Added {len(embeddings)} vectors to ChromaDB collection.")

    def load(self):
        # ChromaDB auto-loads from persist_dir, just verify collection exists
        self.collection = self.client.get_or_create_collection(name="documents")
        print(
            f"[INFO] ChromaDB collection loaded with {self.collection.count()} documents"
        )

    def search(self, query_embedding: np.ndarray, top_k: int = 5):
        results = self.collection.query(
            query_embeddings=query_embedding.tolist(), n_results=top_k
        )
        formatted_results = []
        for i in range(len(results["ids"][0])):
            formatted_results.append(
                {
                    "index": results["ids"][0][i],
                    "distance": (
                        results["distances"][0][i] if results["distances"] else 0
                    ),
                    "metadata": (
                        results["metadatas"][0][i] if results["metadatas"] else None
                    ),
                }
            )
        return formatted_results

    def query(self, query_text: str, top_k: int = 5):
        print(f"[INFO] Querying vector store for: '{query_text}'")
        query_emb = self.model.encode([query_text]).astype("float32")
        return self.search(query_emb, top_k=top_k)
