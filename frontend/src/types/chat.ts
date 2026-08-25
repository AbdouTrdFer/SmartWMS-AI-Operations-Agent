export type ToolCall = {
  name: string;
  status: string;
};

export type Source = {
  id: string;
  title: string;
  kind: string;
};

export type ChatResponse = {
  answer: string;
  tools_used: ToolCall[];
  sources: Source[];
  conversation_id: string;
};
