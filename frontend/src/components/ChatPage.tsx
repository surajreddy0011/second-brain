import { useState, FormEvent, useRef, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import * as api from "../api";
import { ApiError } from "../api";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  sources?: string[];
}

export function ChatPage() {
  const { token } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [question, setQuestion] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleSend(e: FormEvent) {
    e.preventDefault();
    if (!token || !question.trim()) return;

    const userMessage: ChatMessage = { role: "user", content: question };
    setMessages((prev) => [...prev, userMessage]);
    setQuestion("");
    setSending(true);
    setError(null);

    try {
      // Send the conversation so far (before this new message) as history,
      // so the backend can resolve follow-ups like "what date".
      const history = messages.map((m) => ({ role: m.role, content: m.content }));
      const response = await api.sendChatMessage(token, userMessage.content, history);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: response.answer, sources: response.sources },
      ]);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to get a response.");
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="chat-layout">
      <div className="chat-messages">
        {messages.length === 0 && <p className="notes-empty">Ask a question about your notes.</p>}
        {messages.map((msg, i) => (
          <div key={i} className={`chat-bubble ${msg.role}`}>
            <p>{msg.content}</p>
            {msg.sources && msg.sources.length > 0 && (
              <p className="chat-sources">Sources: {msg.sources.join(", ")}</p>
            )}
          </div>
        ))}
        {sending && <div className="chat-bubble assistant chat-typing">Thinking...</div>}
        <div ref={bottomRef} />
      </div>
      {error && <p className="auth-error chat-error">{error}</p>}
      <form className="chat-input-row" onSubmit={handleSend}>
        <input
          type="text"
          placeholder="Ask something about your notes..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          disabled={sending}
        />
        <button type="submit" disabled={sending || !question.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}