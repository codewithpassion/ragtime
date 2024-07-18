import React, { useState } from "react";
import Message from "./Message";
import LoadingIndicator from "./LoadingIndicator";
import { ConversationMessages } from "../lib/types";
import { useChat } from "../hooks/useChat";

const ChatInterface = () => {
  const [message, setMessage] = useState("");
  const initialMessages: ConversationMessages = [
    {
      role: "assistant",
      content: "Hello! I'm RAG AI. How can I assist you today?",
    },
  ];

  const { isLoading, messages, latestMessage, query } =
    useChat(initialMessages);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim()) {
      query(message);
      setMessage("");
    }
  };

  return (
    <div className="flex flex-col h-full bg-gray-900 text-white">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, index) => (
          <Message key={index} content={msg.content} role={msg.role} />
        ))}
        {latestMessage && <Message content={latestMessage} role="assistant" />}
        {isLoading && <LoadingIndicator />}
      </div>
      <div className="border-t border-gray-700">
        <form onSubmit={handleSubmit} className="p-4">
          <div className="flex">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Type your message here..."
              className="flex-1 p-2 bg-gray-800 rounded-l-md focus:outline-none"
            />
            <button
              type="submit"
              className="px-4 py-2 bg-blue-500 rounded-r-md hover:bg-blue-600 focus:outline-none"
            >
              Send
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ChatInterface;
