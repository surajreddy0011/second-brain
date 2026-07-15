import { useState } from "react";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { AuthForm } from "./components/AuthForm";
import { NotesPage } from "./components/NotesPage";
import { ChatPage } from "./components/ChatPage";
import "./index.css";

function AppContent() {
  const { user, loading, logout } = useAuth();
  const [tab, setTab] = useState<"notes" | "chat">("notes");

  if (loading) return <div className="centered">Loading...</div>;

  if (!user) {
    return (
      <div className="centered">
        <AuthForm />
      </div>
    );
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="app-header-left">
          <h1>Second Brain</h1>
          <nav className="app-tabs">
            <button className={tab === "notes" ? "active" : ""} onClick={() => setTab("notes")}>
              Notes
            </button>
            <button className={tab === "chat" ? "active" : ""} onClick={() => setTab("chat")}>
              Chat
            </button>
          </nav>
        </div>
        <div>
          <span className="user-email">{user.email}</span>
          <button onClick={logout}>Log out</button>
        </div>
      </header>
      <main>{tab === "notes" ? <NotesPage /> : <ChatPage />}</main>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}