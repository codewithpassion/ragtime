import argparse
import os

from .tools.data_loader import load_documents, split_documents
from .tools.query import query_rag, run_query_rag
from .tools.database import add_documents_to_db, clear_database
from .tools.server import serve

from dotenv import load_dotenv

load_dotenv()


def main():
    # Check if the database should be cleared (using the --clear flag).
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", action="store_true", help="Run the server.")
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    parser.add_argument("--load", type=str, help="Load data into the database from a directory.")

    args = parser.parse_args()

    if args.load:
        print(f"📥 Loading data from {args.load}")
        documents = load_documents(args.load)
        chunks = split_documents(documents)
        print("📄 Loaded", len(documents), "documents")
        print("📄 Split into", len(chunks), "chunks")
        add_documents_to_db(chunks)

    elif args.reset:
        print("✨ Clearing Database")
        clear_database()

    elif args.server:
        print("🚀 Running the server")
        serve()
        pass

    else:
        print("❔ Please provide your query:")
        query_text = input()
        messages = {"messages": [{"content": query_text, "role": "user"}]}
        for chunk in run_query_rag(messages):
            # check if chunk has a property content:
            if hasattr(chunk, "content"):
                print(chunk.content, end="", flush=True)
            else:
                print("\n\n🔗 Source:", end=" ", flush=True)
                print(chunk)


if __name__ == "__main__":
    main()
