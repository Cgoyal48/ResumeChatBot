# AI ChatBot

A Retrieval-Augmented Generation (RAG) chatbot that answers questions based on PDF documents using ChromaDB for vector storage and Google Gemini for response generation.

## Features

- PDF document loading and chunking
- Vector embeddings using Sentence Transformers (all-MiniLM-L6-v2)
- Vector storage with ChromaDB
- Semantic search for relevant document chunks
- LLM-powered answers using Google Gemini

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your Google API key
```

3. Add PDF files to the `data/` directory

4. Run the application:
```bash
python app.py
```

## Project Structure

```
├── app.py              # Main entry point
├── src/
│   ├── data_loader.py  # PDF loading
│   ├── embedding.py    # Text chunking and embeddings
│   ├── vectorstore.py  # ChromaDB vector storage
│   └── search.py       # RAG search and LLM integration
├── data/               # PDF documents
├── requirements.txt    # Dependencies
└── .env.example        # Environment template
```

## How It Works

1. **Document Loading**: PDFs are loaded from `data/` directory
2. **Chunking**: Documents are split into chunks (1000 chars, 200 overlap)
3. **Embedding**: Each chunk is converted to a vector embedding
4. **Storage**: Vectors are stored in ChromaDB
5. **Query**: User query is embedded and matched to relevant chunks
6. **Generation**: Top chunks are sent to Gemini for answer generation

## License

MIT
