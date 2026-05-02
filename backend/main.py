"""
Resume Chatbot Backend - FastAPI Application
A simple API for chatting with resume PDFs using RAG (Retrieval Augmented Generation)
"""

import os
import shutil
from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Tuple, Optional
from contextlib import asynccontextmanager

from src.search_service import RAGSearch

# Initialize RAG service
rag_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the RAG service on startup"""
    global rag_service
    print("🚀 Initializing RAG service...")
    # Initialize without requiring existing documents
    # User will upload PDF via UI
    rag_service = RAGSearch()
    print("✅ RAG service ready! Waiting for PDF upload...")
    yield
    print("🛑 Shutting down...")


app = FastAPI(
    title="Resume Chatbot API",
    description="Chat with your resume PDF using AI",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""

    query: str
    history: List[Tuple[str, str]] = []  # List of (user_message, bot_response) pairs


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""

    response: str


class UploadResponse(BaseModel):
    """Response model for upload endpoint"""

    message: str
    document_count: int


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Resume Chatbot API is running!", "status": "healthy"}


@app.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a resume PDF file.
    The PDF will be processed and added to the vector store for chatting.

    - **file**: PDF file to upload

    Returns success message and document count.
    """
    global rag_service

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Create uploads directory if it doesn't exist
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)

    # Save uploaded file
    file_path = upload_dir / file.filename
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Process the PDF
        if not rag_service:
            raise HTTPException(status_code=500, detail="RAG service not initialized")

        rag_service.process_uploaded_pdf(str(file_path))
        doc_count = rag_service.vectorstore.collection.count()

        return UploadResponse(
            message=f"Successfully uploaded and processed {file.filename}",
            document_count=doc_count,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")
    finally:
        file.file.close()


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with the uploaded resume PDF.

    - **query**: Your question about the resume
    - **history**: Previous conversation messages (optional)

    Returns the AI's response based on the resume content.
    """
    global rag_service

    if not rag_service:
        raise HTTPException(status_code=500, detail="RAG service not initialized")

    # Check if any documents have been uploaded
    if rag_service.vectorstore.collection.count() == 0:
        raise HTTPException(
            status_code=400, detail="No resume uploaded yet. Please upload a PDF first."
        )

    try:
        answer = rag_service.search_and_summarize(
            query=request.query, history=request.history, top_k=5
        )
        return ChatResponse(response=answer)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")
