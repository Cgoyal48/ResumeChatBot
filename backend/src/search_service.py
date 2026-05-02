"""
RAG Search Service - Core logic for resume chatbot
"""

import os
from typing import List, Tuple

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from .vectorstore import ChromaVectorStore
from .data_loader import load_all_documents

load_dotenv()


class RAGSearch:
    """
    Retrieval-Augmented Generation (RAG) service for chatting with resume PDFs.

    This service:
    1. Loads and indexes resume PDFs into a vector store
    2. Retrieves relevant context based on user queries
    3. Uses Google's Gemini AI to generate contextual responses
    4. Maintains conversation history for follow-up questions
    """

    def __init__(
        self,
        persist_dir: str = "chroma_store",
        embedding_model: str = "all-MiniLM-L6-v2",
        llm_model: str = "gemini-3.1-flash-lite-preview",
    ):
        self.vectorstore = ChromaVectorStore(persist_dir, embedding_model)

        # Just load the vector store - documents will be uploaded via UI
        self.vectorstore.load()

        # Initialize Google Gemini LLM
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")

        self.llm = ChatGoogleGenerativeAI(
            model=llm_model, google_api_key=google_api_key
        )
        print(f"[INFO] Google Generative AI LLM initialized: {llm_model}")

    def search_and_summarize(
        self, query: str, history: List[Tuple[str, str]], top_k: int = 5
    ) -> str:
        """
        Search the resume and generate an AI response.

        Args:
            query: User's question about the resume
            history: List of previous (user_message, bot_response) tuples
            top_k: Number of document chunks to retrieve

        Returns:
            AI-generated response based on resume context
        """
        # Retrieve relevant documents
        results = self.vectorstore.query(query, top_k=top_k)
        texts = [r["metadata"].get("text", "") for r in results if r["metadata"]]
        context = "\n\n".join(texts)

        if not context:
            return "No relevant documents found."

        # Build the prompt with context
        system_prompt = f"""Use the following resume context to answer the user's question.
If the answer cannot be found in the context, say so honestly.

Context:
{context}

Question: """

        # Build message history for conversation context
        messages = []
        for q, a in history:
            messages.append(HumanMessage(content=q))
            messages.append(AIMessage(content=a))
        messages.append(HumanMessage(content=system_prompt + query))

        # Generate response
        response = self.llm.invoke(messages)
        content = getattr(response, "content", None)

        # Handle different response formats
        if content is None:
            content = str(response)
        if isinstance(content, list):
            texts = []
            for item in content:
                if isinstance(item, dict) and "text" in item:
                    texts.append(item["text"])
                else:
                    texts.append(str(item))
            content = "\n".join(texts)
        elif isinstance(content, dict) and "text" in content:
            content = content["text"]

        return str(content)

    def process_uploaded_pdf(self, pdf_path: str) -> None:
        """
        Process an uploaded PDF and add it to the vector store.
        Clears existing documents and rebuilds with the new PDF.

        Args:
            pdf_path: Path to the uploaded PDF file
        """
        print(f"[INFO] Processing uploaded PDF: {pdf_path}")

        # Clear existing collection
        self.vectorstore.clear_collection()

        # Load and process the new PDF
        docs = load_all_documents(pdf_path)
        if not docs:
            raise ValueError("No documents could be loaded from the PDF")

        # Build vector store with new documents
        self.vectorstore.build_from_documents(docs)
        print(f"[INFO] Successfully processed PDF with {len(docs)} pages")
