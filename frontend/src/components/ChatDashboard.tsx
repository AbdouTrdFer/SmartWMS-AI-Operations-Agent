import {
  AlertTriangle,
  ArrowRight,
  Bot,
  Boxes,
  ClipboardList,
  FileText,
  Loader2,
  PackageSearch,
  Send,
  ShieldCheck,
  Sparkles
} from "lucide-react";
import { FormEvent, useMemo, useState } from "react";

import { sendChatMessage } from "@/services/api";
import type { ChatResponse } from "@/types/chat";

const examples = [
  {
    label: "Replenishment",
    prompt: "Why is SKU-102 a high replenishment priority at WH-NJ?",
    icon: AlertTriangle
  },
  {
    label: "Low stock",
    prompt: "Show low stock items in WH-NJ",
    icon: Boxes
  },
  {
    label: "Damaged goods",
    prompt: "What is the damaged goods procedure?",
    icon: FileText
  },
  {
    label: "Open orders",
    prompt: "List open orders for WH-TX",
    icon: ClipboardList
  }
];

const metrics = [
  { label: "Mode", value: "Demo", tone: "text-emerald-700" },
  { label: "Access", value: "Read-only", tone: "text-sky-700" },
  { label: "Data", value: "Synthetic", tone: "text-amber-700" }
];

export function ChatDashboard() {
  const [message, setMessage] = useState(examples[0].prompt);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [response, setResponse] = useState<ChatResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const activeTools = useMemo(() => response?.tools_used ?? [], [response]);
  const activeSources = useMemo(() => response?.sources ?? [], [response]);

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
    <main className="min-h-screen bg-[#f3f6f8] text-slate-950">
      <div className="mx-auto flex max-w-7xl flex-col gap-6 px-4 py-5 sm:px-6 lg:px-8">
        <header className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
          <div className="grid gap-0 lg:grid-cols-[minmax(0,1fr)_380px]">
            <div className="flex flex-col justify-between gap-8 p-6 sm:p-8">
              <div className="space-y-4">
                <div className="inline-flex w-fit items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-semibold uppercase text-emerald-700">
                  <ShieldCheck className="h-3.5 w-3.5" />
                  SmartWMS
                </div>
                <div>
                  <h1 className="max-w-3xl text-4xl font-semibold tracking-normal text-slate-950 sm:text-5xl">
                    Operations Command Center
                  </h1>
                  <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600 sm:text-base">
                    Inventory signals, order context, and warehouse policy references in one
                    controlled AI workspace.
                  </p>
                </div>
              </div>

              <div className="grid gap-3 sm:grid-cols-3">
                {metrics.map((metric) => (
                  <div key={metric.label} className="rounded-md border border-slate-200 bg-slate-50 p-3">
                    <p className="text-xs font-medium uppercase text-slate-500">{metric.label}</p>
                    <p className={`mt-1 text-lg font-semibold ${metric.tone}`}>{metric.value}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="border-t border-slate-200 bg-slate-950 p-6 text-white lg:border-l lg:border-t-0">
              <div className="flex h-full flex-col justify-between gap-8">
                <div>
                  <div className="flex items-center gap-2 text-sm font-semibold text-emerald-300">
                    <Bot className="h-4 w-4" />
                    Agent status
                  </div>
                  <p className="mt-4 text-3xl font-semibold">{isLoading ? "Analyzing" : "Ready"}</p>
                  <p className="mt-2 text-sm leading-6 text-slate-300">
                    Answers are grounded in approved read-only tools and synthetic policy sources.
                  </p>
                </div>
                <div className="rounded-md border border-white/10 bg-white/5 p-4">
                  <p className="text-xs uppercase text-slate-400">Conversation</p>
                  <p className="mt-1 truncate text-sm text-slate-100">
                    {conversationId ?? "New session"}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </header>

        <section className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_340px]">
          <div className="rounded-lg border border-slate-200 bg-white shadow-sm">
            <form onSubmit={handleSubmit} className="border-b border-slate-200 p-5 sm:p-6">
              <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <label htmlFor="message" className="text-sm font-semibold text-slate-900">
                  Operations question
                </label>
                <span className="text-xs text-slate-500">{message.length}/2000</span>
              </div>

              <div className="mt-3 overflow-hidden rounded-lg border border-slate-300 bg-white transition focus-within:border-emerald-500 focus-within:ring-4 focus-within:ring-emerald-100">
                <textarea
                  id="message"
                  className="min-h-36 w-full resize-y border-0 bg-transparent p-4 text-sm leading-6 text-slate-900 outline-none"
                  value={message}
                  maxLength={2000}
                  onChange={(event) => setMessage(event.target.value)}
                />
                <div className="flex items-center justify-between border-t border-slate-200 bg-slate-50 px-3 py-2">
                  <div className="flex items-center gap-2 text-xs text-slate-500">
                    <Sparkles className="h-3.5 w-3.5 text-amber-600" />
                    Grounded response
                  </div>
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="inline-flex h-9 items-center gap-2 rounded-md bg-slate-950 px-4 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:bg-slate-400"
                  >
                    {isLoading ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Send className="h-4 w-4" />
                    )}
                    {isLoading ? "Analyzing" : "Send"}
                  </button>
                </div>
              </div>

              <div className="mt-4 grid gap-2 sm:grid-cols-2 xl:grid-cols-4">
                {examples.map((example) => {
                  const Icon = example.icon;
                  return (
                    <button
                      key={example.label}
                      type="button"
                      onClick={() => setMessage(example.prompt)}
                      className="group flex min-h-20 flex-col justify-between rounded-md border border-slate-200 bg-white p-3 text-left text-sm transition hover:-translate-y-0.5 hover:border-emerald-300 hover:shadow-md"
                    >
                      <span className="flex items-center justify-between gap-2">
                        <Icon className="h-4 w-4 text-slate-500 group-hover:text-emerald-700" />
                        <ArrowRight className="h-4 w-4 text-slate-300 group-hover:text-emerald-700" />
                      </span>
                      <span className="font-medium text-slate-800">{example.label}</span>
                    </button>
                  );
                })}
              </div>
            </form>

            {error ? (
              <div className="mx-5 mt-5 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700 sm:mx-6">
                {error}
              </div>
            ) : null}

            <article className="p-5 sm:p-6">
              <div className="flex items-center gap-2">
                <PackageSearch className="h-4 w-4 text-emerald-700" />
                <h2 className="text-sm font-semibold uppercase text-slate-500">Answer</h2>
              </div>
              <div className="mt-4 min-h-64 rounded-lg border border-slate-200 bg-slate-50 p-5">
                {isLoading ? (
                  <div className="space-y-3">
                    <div className="h-3 w-2/3 animate-pulse rounded bg-slate-200" />
                    <div className="h-3 w-full animate-pulse rounded bg-slate-200" />
                    <div className="h-3 w-5/6 animate-pulse rounded bg-slate-200" />
                  </div>
                ) : (
                  <pre className="whitespace-pre-wrap font-sans text-sm leading-7 text-slate-800">
                    {response?.answer ?? "Ask a question to review WMS facts and policy context."}
                  </pre>
                )}
              </div>
            </article>
          </div>

          <aside className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
            <h2 className="text-sm font-semibold uppercase text-slate-500">Tools and Sources</h2>

            <div className="mt-5">
              <h3 className="text-sm font-semibold text-slate-900">Tools used</h3>
              <ul className="mt-3 space-y-2 text-sm">
                {activeTools.map((tool) => (
                  <li
                    key={tool.name}
                    className="flex items-center justify-between rounded-md border border-slate-200 bg-slate-50 px-3 py-2 text-slate-700"
                  >
                    <span>{tool.name}</span>
                    <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-medium text-emerald-700">
                      {tool.status}
                    </span>
                  </li>
                ))}
                {!activeTools.length ? <li className="text-slate-500">None yet</li> : null}
              </ul>
            </div>

            <div className="mt-6">
              <h3 className="text-sm font-semibold text-slate-900">Sources</h3>
              <ul className="mt-3 space-y-2 text-sm">
                {activeSources.map((source) => (
                  <li
                    key={source.id}
                    className="rounded-md border border-slate-200 bg-white px-3 py-2 text-slate-700"
                  >
                    <p className="font-medium">{source.title}</p>
                    <p className="mt-1 text-xs text-slate-500">{source.kind}</p>
                  </li>
                ))}
                {!activeSources.length ? <li className="text-slate-500">None yet</li> : null}
              </ul>
            </div>
          </aside>
        </section>
      </div>
    </main>
  );
}
