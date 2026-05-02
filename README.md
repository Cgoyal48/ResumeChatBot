# Resume Chatbot - Full Stack AI Application

A beginner-friendly full-stack chatbot that lets you chat with resume PDFs using AI. Built with **FastAPI** (backend), **React + TypeScript + Material UI** (frontend), and **Google Gemini** for intelligent responses.

## Features

- **Modern Web UI**: Clean chat interface built with React and Material UI
- **PDF Processing**: Automatically loads and processes resume PDFs
- **AI-Powered Chat**: Ask questions about the resume and get contextual answers
- **Conversation Memory**: The bot remembers your previous questions
- **RAG Architecture**: Uses Retrieval-Augmented Generation for accurate responses

## Project Structure

```
├── backend/                 # FastAPI Backend
│   ├── main.py             # API entry point with /chat endpoint
│   ├── src/
│   │   ├── search_service.py   # RAG logic and LLM integration
│   │   ├── vectorstore.py    # ChromaDB vector storage
│   │   ├── embedding.py      # Text chunking & embeddings
│   │   └── data_loader.py    # PDF loading
│   ├── data/               # Put your resume PDFs here
│   └── requirements.txt    # Python dependencies
│
├── frontend/               # React + TypeScript Frontend
│   ├── src/
│   │   ├── components/
│   │   │   └── ChatUI.tsx    # Main chat interface
│   │   ├── App.tsx
│   │   └── main.tsx
│   └── package.json        # Node dependencies
│
├── data/                   # Legacy data folder (or use backend/data/)
└── README.md
```

## Quick Start

### 1. Setup Environment

Create a `.env` file in the `backend/` folder:

```bash
cd backend
cp .env.example .env
# Edit .env and add your Google API Key
```

### 2. Start the Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### 3. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

The web app will open at `http://localhost:5173`

## How It Works (Simple Explanation)

1. **PDF Loading**: Your resume PDF is loaded and split into text chunks
2. **Embeddings**: Each chunk is converted to a "vector" (a list of numbers that represents the meaning)
3. **Vector Store**: These vectors are stored in ChromaDB for fast searching
4. **User Question**: When you ask a question, it's also converted to a vector
5. **Similarity Search**: The system finds the most similar chunks from the resume
6. **AI Response**: Google Gemini uses those chunks to answer your question

## Learning Resources

This project demonstrates:

- **Backend**: FastAPI, REST APIs, environment variables
- **Frontend**: React hooks (useState, useEffect), Material UI components
- **AI/ML**: RAG pattern, vector embeddings, LLM integration
- **Full Stack**: Connecting frontend to backend with HTTP requests

## Customization

- **Change the PDF**: Replace `backend/data/Resume.pdf` with your own resume
- **Change the model**: Edit `llm_model` in `backend/src/search_service.py`
- **Change the UI**: Edit `frontend/src/components/ChatUI.tsx`

## License

MIT - Free for learning and building!
