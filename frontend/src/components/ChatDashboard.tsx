import { FormEvent, useState } from "react";

import { sendChatMessage } from "@/services/api";
import type { ChatResponse } from "@/types/chat";

const examples = [
  "Why is SKU-102 a high reorder priority at WH-NJ?",
  "Show low stock items in WH-NJ",
  "What is the damaged goods procedure?",
  "List open orders for WH-TX"
];

export function ChatDashboard() {
  const [message, setMessage] = useState(examples[0]);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [response, setResponse] = useState<ChatResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsLoading(true);
    try {
      const result = await sendChatMessage(message, conversationId);
      setResponse(result);
      setConversationId(result.conversation_id);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unexpected error");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-steel text-ink">
      <div className="mx-auto flex max-w-6xl flex-col gap-5 px-5 py-6">
        <header className="flex flex-col gap-1 border-b border-slate-300 pb-4">
          <p className="text-sm font-semibold uppercase tracking-wide text-signal">SmartWMS</p>
          <h1 className="text-3xl font-semibold">AI Operations Agent</h1>
          <p className="max-w-3xl text-sm text-slate-600">
            Demo-mode assistant for inventory, reorder, open order, and warehouse policy questions.
          </p>
        </header>

        <section className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_300px]">
          <div className="rounded border border-slate-300 bg-white p-4 shadow-sm">
            <form onSubmit={handleSubmit} className="flex flex-col gap-3">
              <label htmlFor="message" className="text-sm font-medium">
                Ask an operations question
              </label>
              <textarea
                id="message"
                className="min-h-32 resize-y rounded border border-slate-300 p-3 text-sm outline-none focus:border-signal focus:ring-2 focus:ring-signal/20"
                value={message}
                maxLength={2000}
                onChange={(event) => setMessage(event.target.value)}
              />
              <div className="flex flex-wrap gap-2">
                {examples.map((example) => (
                  <button
                    key={example}
                    type="button"
                    onClick={() => setMessage(example)}
                    className="rounded border border-slate-300 px-3 py-1.5 text-xs text-slate-700 hover:border-signal hover:text-signal"
                  >
                    {example}
                  </button>
                ))}
              </div>
              <button
                type="submit"
                disabled={isLoading}
                className="w-fit rounded bg-signal px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-slate-400"
              >
                {isLoading ? "Analyzing..." : "Send"}
              </button>
            </form>

            {error ? (
              <div className="mt-4 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                {error}
              </div>
            ) : null}

            <article className="mt-5 min-h-56 rounded border border-slate-200 bg-slate-50 p-4">
              <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Answer</h2>
              <pre className="mt-3 whitespace-pre-wrap font-sans text-sm leading-6 text-slate-800">
                {isLoading
                  ? "Loading WMS context..."
                  : response?.answer ?? "No response yet. Try one of the example questions."}
              </pre>
            </article>
          </div>

          <aside className="rounded border border-slate-300 bg-white p-4 shadow-sm">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
              Tools and Sources
            </h2>
            <div className="mt-4">
              <h3 className="text-sm font-semibold">Tools used</h3>
              <ul className="mt-2 space-y-2 text-sm text-slate-700">
                {(response?.tools_used.length ? response.tools_used : []).map((tool) => (
                  <li key={tool.name} className="rounded border border-slate-200 px-2 py-1">
                    {tool.name}
                  </li>
                ))}
                {!response?.tools_used.length ? <li className="text-slate-500">None yet</li> : null}
              </ul>
            </div>
            <div className="mt-5">
              <h3 className="text-sm font-semibold">Sources</h3>
              <ul className="mt-2 space-y-2 text-sm text-slate-700">
                {(response?.sources.length ? response.sources : []).map((source) => (
                  <li key={source.id} className="rounded border border-slate-200 px-2 py-1">
                    {source.title}
                  </li>
                ))}
                {!response?.sources.length ? <li className="text-slate-500">None yet</li> : null}
              </ul>
            </div>
          </aside>
        </section>
      </div>
    </main>
  );
}
