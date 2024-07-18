import { useCallback, useMemo, useState } from "react";
import { ConversationMessage, ConversationMessages } from "../lib/types";
import { EventSourceParserStream } from "eventsource-parser/stream";

export type ApiData = {
  stream: boolean;
  messages: ConversationMessages;
};

const useChat = (initialMessages: ConversationMessages) => {
  const [isLoading, setIsLoading] = useState(false);
  const [latestMessage, setLatestMessage] = useState<string>("");
  const [messages, setMessages] = useState<ConversationMessages>([
    ...initialMessages,
  ]);

  const obtainAPIResponse = useCallback(
    async (apiRoute: string, apiData: ApiData) => {
      const apiResponse = await fetch(apiRoute, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(apiData),
      });

      if (!apiResponse.body) return;

      const reader = apiResponse.body
        .pipeThrough(new TextDecoderStream())
        .pipeThrough(new EventSourceParserStream())
        .getReader();

      let incomingMessage = "";

      for (;;) {
        const { value, done } = await reader.read();
        if (done) {
          setMessages((messages) => [
            ...messages,
            { role: "assistant", content: incomingMessage },
          ]);
          setLatestMessage("");
          break;
        }
        if (value) {
          const eventName = value.event;
          if (eventName === "content_block_delta") {
            const data = JSON.parse(value.data);
            if (data?.delta?.text) {
              if (data.delta.text.startsWith('[{"source"')) {
                console.log("Sources: ", data.delta.text);
              } else {
                incomingMessage += data.delta.text;
                setLatestMessage(incomingMessage);
                setIsLoading(false);
              }
            }
          }
        }
      }
    },
    []
  );

  const query = useCallback(
    async (message: string) => {
      setIsLoading(true);
      const queryMessage: ConversationMessage = {
        role: "human",
        content: message,
      };
      const currentMessages = [...messages, queryMessage];

      setMessages((prevMessages) => [...prevMessages, queryMessage]);
      await obtainAPIResponse("http://localhost:5000/v1/messages", {
        stream: true,
        messages: currentMessages,
      });
    },
    [messages, obtainAPIResponse]
  );

  return useMemo(
    () => ({
      latestMessage,
      messages,
      query,
      isLoading,
    }),
    [isLoading, latestMessage, messages, query]
  );
};

export { useChat };
