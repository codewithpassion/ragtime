from ..tools.youtube_transcript_data_loader import YoutubeTranscriptDataLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.document import Document

CHUNK_SIZE = 800
CHUNK_OVERLAP = 80


def load_documents(directory: str):
    """Loads documents from the specified directory.

    Args:
        directory (str): The directory path where the documents are located.

    Returns:
        None
    """
    loader = YoutubeTranscriptDataLoader(file_glob=f"{directory}/*.json")
    return loader.load()


def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        is_separator_regex=False,
    )
    chunks = text_splitter.split_documents(documents)
    # Usage

    matched_chunks = []
    for document in documents:
        doc_chunks = list(
            filter(lambda x: x.metadata["id"] == document.metadata["id"], chunks)
        )
        matched_chunks.extend(match_chunks_with_snippets(doc_chunks, document))

    return matched_chunks


def match_chunks_with_snippets(chunks, original_document):
    snippets = original_document.metadata["snippets"]

    for chunk in chunks:
        found = False
        matching_snippets = []
        for snippet in snippets:
            if snippet["text"] in chunk.page_content:
                matching_snippets.append(snippet)
                found = True
            else:
                if found:
                    break

        chunk.metadata["snippets"] = matching_snippets

    return chunks
