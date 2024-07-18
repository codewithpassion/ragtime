import json
import glob
from langchain.document_loaders.base import BaseLoader
from langchain.schema import Document


class YoutubeTranscriptDataLoader(BaseLoader):
    def __init__(self, file_glob):
        self.file_glob = file_glob

    def load(self):
        documents = []
        for file_path in glob.glob(self.file_glob):
            with open(file_path, "r") as file:
                data = json.load(file)

            metadata = data["metadata"]
            full_transcript = " ".join([entry["text"] for entry in data["transcript"]])

            snippets = []
            current_snippet = []
            current_duration = 0

            for entry in data["transcript"]:
                current_snippet.append(entry["text"])
                current_duration += entry["duration"]

                if current_duration >= 15:
                    snippets.append(
                        {
                            "text": " ".join(current_snippet),
                            "start": data["transcript"][len(snippets)]["start"],
                            "duration": current_duration,
                        }
                    )
                    current_snippet = []
                    current_duration = 0

            if current_snippet:
                snippets.append(
                    {
                        "text": " ".join(current_snippet),
                        "start": data["transcript"][len(snippets)]["start"],
                        "duration": current_duration,
                    }
                )

            metadata["snippets"] = snippets
            metadata["source"] = file_path
            # metadata['metadata'] = data['metadata']
            metadata["id"] = data["metadata"]["id"]

            documents.append(Document(page_content=full_transcript, metadata=metadata))

        return documents
