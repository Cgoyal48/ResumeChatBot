from src.search import RAGSearch


def main():
    rag_search = RAGSearch()
    query = "What is the name of the person?"
    summary = rag_search.search_and_summarize(query, top_k=3)
    print("Summary:", summary)


if __name__ == "__main__":
    main()
