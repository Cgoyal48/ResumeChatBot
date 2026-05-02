from pathlib import Path
from typing import List, Any
from langchain_community.document_loaders import PyPDFLoader


def load_all_documents(data_path: str) -> List[Any]:
    """
    Load PDF documents from a directory or single file.
    Supported: PDF

    Args:
        data_path: Path to a directory or a single PDF file
    """
    path = Path(data_path).resolve()
    print(f"[DEBUG] Data path: {path}")
    documents = []

    # Check if it's a single file
    if path.is_file() and path.suffix.lower() == ".pdf":
        print(f"[DEBUG] Loading single PDF: {path}")
        try:
            loader = PyPDFLoader(str(path))
            loaded = loader.load()
            print(f"[DEBUG] Loaded {len(loaded)} pages from {path}")
            documents.extend(loaded)
        except Exception as e:
            print(f"[ERROR] Failed to load PDF {path}: {e}")
    # Otherwise treat as directory
    elif path.is_dir():
        pdf_files = list(path.glob("**/*.pdf"))
        print(
            f"[DEBUG] Found {len(pdf_files)} PDF files: {[str(f) for f in pdf_files]}"
        )
        for pdf_file in pdf_files:
            print(f"[DEBUG] Loading PDF: {pdf_file}")
            try:
                loader = PyPDFLoader(str(pdf_file))
                loaded = loader.load()
                print(f"[DEBUG] Loaded {len(loaded)} pages from {pdf_file}")
                documents.extend(loaded)
            except Exception as e:
                print(f"[ERROR] Failed to load PDF {pdf_file}: {e}")
    else:
        print(f"[ERROR] Invalid path: {path}")

    print(f"[DEBUG] Total loaded documents: {len(documents)}")
    return documents
