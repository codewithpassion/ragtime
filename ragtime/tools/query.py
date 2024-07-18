import os
from ..tools.database import query
from langchain.prompts import ChatPromptTemplate

# from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
import asyncio
import math

from dotenv import load_dotenv

from .utils import get_last_user_message

load_dotenv()

PROMPT_TEMPLATE = """
You are an AI assistant that has a broad database of information from a youtube channel.
Bellow you will find the context of the information retrieved from a vector search in the database.
Answer the question based on this data only and the message history.

# context
{context}

# Message history:
{message_history}


# task
Answer this user questions based on the data above: {question}

# formatting
Format your answers in markdown format.

# Instructions
If you can't answer the question, you can say :
- "I'm not sure - I haven't been trained to answer this question".

Don't mention these words or phrases:
- 'it appears to be'
- context
- Based on the information provided.
- the information provided

Instead just answer the question directly as if you know the answer by yourself.

"""


# DEFAULT_MODEL = "gpt-4o"
DEFAULT_MODEL = "claude-3-5-sonnet-20240620"


def strip_first_assistant_message(messages):
    if messages["messages"][0]["role"] == "assistant":
        messages["messages"] = messages["messages"][1:]
    return messages


def create_message_history(messages):
    return "\n".join([f"{m['role']}: {m['content']}" for m in messages["messages"]])


async def query_rag(messages):
    query_str = get_last_user_message(messages)

    # Search the DB.
    results = query(query_str, k=5)

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)

    message_history = create_message_history(messages)

    prompt = prompt_template.format(context=context_text, question=query_str, message_history=message_history)

    messages["messages"][-1]["content"] = prompt

    model = ChatAnthropic(model=DEFAULT_MODEL, api_key=os.environ["ANTHROPIC_API_KEY"])
    # only get the last user message
    query_messages = [messages["messages"][-1]]

    print("Query messages", query_messages)

    for chunk in model.stream(query_messages):
        yield chunk

    sources = list()
    for doc, _score in results:
        id = doc.metadata.get("id", None).split(":")[0]
        title = doc.metadata.get("title", None)
        source = f"https://www.youtube.com/watch?v={id}"

        channel = doc.metadata.get("channel", None)
        published_at = doc.metadata.get("published_at", None)

        snippets = doc.metadata.get("snippets", None)
        if snippets:
            start_time = snippets[0]["start"]
            source_timestamped = f"https://www.youtube.com/watch?v={id}&t={math.floor(start_time)}"
        sources.append(
            {
                "source": source,
                "source_timestamped": source_timestamped,
                "snippets": snippets,
                "title": title,
                "id": id,
                "channel": channel,
                "published_at": published_at,
            }
        )

    yield sources


def run_query_rag(query_text):
    return stream_results(query_rag(query_text))


def stream_results(async_gen):
    loop = asyncio.get_event_loop()
    try:
        while True:
            yield loop.run_until_complete(anext(async_gen))
    except StopAsyncIteration:
        pass


def run_query_rag_sync(query_text):
    return asyncio.run(async_generator_to_list(query_rag(query_text)))


async def async_generator_to_list(async_gen):
    return [item async for item in async_gen]
