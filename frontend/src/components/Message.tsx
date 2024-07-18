import React from "react";
import ReactMarkdown from "react-markdown";
import { ConversationMessage } from "../lib/types";

export type MessageProps = ConversationMessage;

const Message = ({ content, role }: MessageProps) => {
  const isHuman = role === "human";
  return (
    <div className={`flex ${isHuman ? "justify-end" : "justify-start"}`}>
      <div
        className={`rounded-lg p-3 max-w-[80%] ${
          isHuman ? "bg-gray-700" : "bg-blue-500"
        }`}
      >
        <ReactMarkdown className="prose prose-invert max-w-none">
          {content}
        </ReactMarkdown>
      </div>
    </div>
  );
};

export default Message;
