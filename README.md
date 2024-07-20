# ragtime

An experimental RAG application.

1. Python backend, loading, querying data into a vector store, providing a HTTP API
2. A React frontend to interact with the agent querying the data




## Installation

Make sure you have [poetry](https://python-poetry.org/docs/#installation) and [Bun](https://bun.sh) installed!

```
poetry install

cd frontend

bun install
```

## Running

```
cp .env.example .env
<Add your API keys to .env>

docker compose up
poetry run ragtime --serve &
cd frontend
bun vite dev
```


# Data loading

To load data, find a youtube channel or playlist, for example
[Life Lessons, Tips, and Advice from Tim Ferriss
View full playlist](https://www.youtube.com/playlist?list=PLuu6fDad2eJyj3ZHfm9TlWWUNmqhdN2iZ).

Then you can run:
```
poetry run yt-tools https://www.youtube.com/playlist?list=PLuu6fDad2eJyj3ZHfm9TlWWUNmqhdN2iZ
```

This will create a directory based on the channel name, eg `Tim Ferriss` and save all video's transcripts
and metadata as JSON files in this folder. 

Then you can load the data with:
(Make sure you ran `docker compose up`)
```
poetry run ragtime --load "./Tim Ferriss"
```
