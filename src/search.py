import os

from dotenv import load_dotenv
from src.vectorstore import ChromaVectorStore
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


class RAGSearch:
    def __init__(
        self,
        persist_dir: str = "chroma_store",
        embedding_model: str = "all-MiniLM-L6-v2",
        llm_model: str = "gemini-2.5-flash",
    ):
        self.vectorstore = ChromaVectorStore(persist_dir, embedding_model)
        # Check if collection has documents, otherwise build from data
        if self.vectorstore.collection.count() == 0:
            from src.data_loader import load_all_documents

            docs = load_all_documents("data")
            self.vectorstore.build_from_documents(docs)
        else:
            self.vectorstore.load()
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        self.llm = ChatGoogleGenerativeAI(
            model=llm_model, google_api_key=google_api_key
        )
        print(f"[INFO] Google Generative AI LLM initialized: {llm_model}")

    def search_and_summarize(self, query: str, top_k: int = 5) -> str:
        results = self.vectorstore.query(query, top_k=top_k)
        texts = [r["metadata"].get("text", "") for r in results if r["metadata"]]
        context = "\n\n".join(texts)
        if not context:
            return "No relevant documents found."
        prompt = f"""Summarize the following context for the query: '{query}'\n\nContext:\n{context}\n\nSummary:"""
        response = self.llm.invoke([prompt])
        return response.content
