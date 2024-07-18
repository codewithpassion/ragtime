export type Roles = "human" | "assistant";

export type ConversationMessage = {
  content: string;
  role: Roles;
};

export type ConversationMessages = ConversationMessage[];
