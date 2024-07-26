import asyncio
from flask import Flask, Response, request, jsonify, url_for
from flask_sse import sse
import jsonpickle

from langchain_core.messages import AIMessageChunk

from .utils import get_last_user_message
from .query import run_query_rag, run_query_rag_sync, DEFAULT_MODEL
import uuid
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/v1/*": {"origins": "http://localhost:*"}})
# app.register_blueprint(sse, url_prefix="/v1/messages")


def serve():
    print("🚀 Running the server")

    app.run(debug=True)


@app.route("/v1/messages", methods=["POST"])
def get_data():
    data = request.json

    print(f"Data: {data}")
    with app.app_context():
        if data and isinstance(data.get("messages"), list):
            prompt = get_last_user_message(data)

            if prompt:
                if data and data.get("stream") is True:

                    def eventStream():
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        id = str(uuid.uuid4())
                        yield "event: message_start\ndata: {}\n\n".format(
                            jsonpickle.encode(
                                {
                                    "id": id,
                                    "type": "message",
                                    "role": "assistant",
                                    "model": DEFAULT_MODEL,
                                    "content": "[]",
                                    "stop_reason": None,
                                    "stop_sequence": None,
                                    "usage": {},
                                }
                            )
                        )
                        yield "event: content_block_start\ndat: {}\n\n".format(
                            jsonpickle.encode(
                                {
                                    "type": "content_block_start",
                                    "index": 0,
                                    "content_block": {"type": "text", "text": ""},
                                }
                            )
                        )

                        for chunk in run_query_rag(data):
                            yield "event: content_block_delta\ndata: {}\n\n".format(
                                serialize_aimessagechunk(chunk, id)
                            )
                        yield "event: message_delta\ndata: {}\n\n".format(
                            jsonpickle.encode(
                                {
                                    "type": "message_delta",
                                    "delta": {
                                        "stop_reason": "end_turn",
                                        "stop_sequence": None,
                                    },
                                    "usage": {},
                                }
                            )
                        )
                        yield "event: content_block_stop\n data: {}\n\n".format(
                            jsonpickle.encode(
                                {"type": "content_block_stop", "index": 0}
                            )
                        )
                        yield 'event: message_stop\ndata: {"type":"message_stop"}\n\n'

                    # sse.
                    return Response(eventStream(), content_type="text/event-stream")
                else:
                    data = run_query_rag_sync(data)
                    message_text = ""
                    for chunk in data:
                        if hasattr(chunk, "content"):
                            message_text += chunk.content
                        else:
                            message_text += "\n\n{}".format(jsonpickle.encode(chunk))

                    return jsonify(
                        {
                            "id": "msg_01NFyAMrWottunZ2prGYNUUJ",
                            "type": "message",
                            "role": "assistant",
                            "model": "claude-3-5-sonnet-20240620",
                            "content": [
                                {
                                    "type": "text",
                                    "text": message_text,
                                }
                            ],
                            "stop_reason": "end_turn",
                            "stop_sequence": None,
                            "usage": {},
                        }
                    )
        else:
            print("XXXXXXXXXXXXXXXXXX")
            return jsonify({"message": "No messages found"})


def serialize_aimessagechunk(chunk: AIMessageChunk, id: str):
    data = {
        "id": id,
        "type": "content_block_delta",
        "index": 0,
        "delta": {"type": "text_delta", "text": ""},
    }
    if not hasattr(chunk, "content"):
        content = jsonpickle.encode(chunk)
        data["delta"]["text"] = content
        # return chunk
    else:
        if chunk.content.startswith('"'):
            data["delta"]["text"] = jsonpickle.decode(chunk.content)
        else:
            data["delta"]["text"] = chunk.content

    return jsonpickle.encode(data)
