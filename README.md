# ragtime

An experimental RAG application.

1. Python backend, loading, querying data into a vector store, providing a HTTP API
2. A React frontend to interact with the agent querying the data


## Installation

```
poetry install

cd frontend

bun install
```

## Running
```
docker compose up
poetry run ragtime --serve &
cd frontend
bun vite dev
```
