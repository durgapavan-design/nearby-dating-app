import { FormEvent, useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api, ChatMessage, wsUrl } from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function Chat() {
  const { matchId } = useParams<{ matchId: string }>();
  const { me } = useAuth();
  const navigate = useNavigate();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [connected, setConnected] = useState(false);
  const socketRef = useRef<WebSocket | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!matchId) return;

    api.getMessages(matchId).then(setMessages).catch(() => navigate("/matches", { replace: true }));

    const socket = new WebSocket(wsUrl(matchId));
    socketRef.current = socket;

    socket.onopen = () => setConnected(true);
    socket.onclose = () => setConnected(false);
    socket.onmessage = (event) => {
      const message: ChatMessage = JSON.parse(event.data);
      setMessages((prev) => [...prev, message]);
    };

    return () => socket.close();
  }, [matchId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async (e: FormEvent) => {
    e.preventDefault();
    const content = draft.trim();
    if (!content || !matchId) return;
    setDraft("");

    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({ content }));
    } else {
      const message = await api.sendMessage(matchId, content);
      setMessages((prev) => [...prev, message]);
    }
  };

  return (
    <div className="page chat-page">
      <div className="chat-header">
        <button className="back-btn" onClick={() => navigate("/matches")}>
          ← Back
        </button>
        {!connected && <span className="hint">reconnecting...</span>}
      </div>
      <div className="chat-messages">
        {messages.map((m) => (
          <div key={m.id} className={`chat-bubble ${m.sender_id === me?.id ? "chat-bubble-mine" : ""}`}>
            {m.content}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
      <form className="chat-input-row" onSubmit={send}>
        <input
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder="Type a message..."
          autoFocus
        />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}
