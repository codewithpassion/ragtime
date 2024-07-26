import os
import psycopg2
from pgvector.psycopg2 import register_vector
from dotenv import load_dotenv
from langchain_postgres.vectorstores import PGVector

from langchain_openai.embeddings import OpenAIEmbeddings

from langchain_community.embeddings import OllamaEmbeddings


def get_embeddings():
    if os.environ.get("EMBEDDINGS") == "openai":
        return OpenAIEmbeddings(
            model="gpt-4o-mini", base_url=os.environ.get("EMBEDDINGS_BASE_URL") or None
        )
    else:
        return OllamaEmbeddings(
            model="llama3.1", base_url=os.environ.get("EMBEDDINGS_BASE_URL")
        )


load_dotenv(verbose=True)

connection_string = os.environ["PG_CONNECTION_STRING"]
print(f"Connection String: {connection_string}")

collection_name = "ragtime"
embeddings = (
    get_embeddings()
)  # OllamaEmbeddings(model="llama3.1", base_url="http://dell.home.arpa:11434")

vectorstore = PGVector(
    embeddings=embeddings,
    connection=connection_string,
    collection_name=collection_name,
    use_jsonb=True,
    async_mode=False,
    create_extension=True,
)


def clear_database():
    vectorstore.delete_collection()

    print("✨ Database Cleared")


def add_documents_to_db(chunks: list):
    # Add the chunks to the database.
    print(f"📄 Adding {len(chunks)} documents to the database")
    print(f"Connection String: {connection_string}")

    chunks_with_ids = calculate_chunk_ids(chunks)

    # Add or Update the documents.
    existing_ids = get_document_ids(connection_string)
    print(f"Number of existing documents in DB: {len(existing_ids)}")
    print(f"First 5 existing IDs: {existing_ids[:5]}")

    # Only add documents that don't exist in the DB.
    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks):
        print(f"👉 Adding new documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        vectorstore.add_documents(new_chunks, ids=new_chunk_ids)
    else:
        print("✅ No new documents to add")

    pass


def calculate_chunk_ids(chunks):
    for idx, chunk in enumerate(chunks):
        source_id = chunk.metadata.get("id")

        # Calculate the chunk ID.
        chunk_id = f"{source_id}:{idx}"

        # Add it to the page meta-data.
        chunk.metadata["id"] = chunk_id

    return chunks


def get_document_ids(connection_string):
    # Establish a connection to the database
    conn = psycopg2.connect(connection_string)
    cur = conn.cursor()
    # Execute a SQL query to retrieve the IDs
    cur.execute("SELECT id FROM langchain_pg_embedding")
    # Fetch all the results
    ids = cur.fetchall()
    ids = list(map(lambda x: x[0], ids))
    cur.close()
    conn.close()

    # Return the IDs
    return ids


def query(query_text: str, k: int = 5):
    return vectorstore.similarity_search_with_score(query_text, k=k)
