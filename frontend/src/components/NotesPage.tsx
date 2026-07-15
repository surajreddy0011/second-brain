import { useEffect, useState, FormEvent } from "react";
import { useAuth } from "../context/AuthContext";
import * as api from "../api";
import { ApiError } from "../api";

export function NotesPage() {
  const { token } = useAuth();
  const [notes, setNotes] = useState<api.Note[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    api
      .listNotes(token)
      .then(setNotes)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load notes."))
      .finally(() => setLoading(false));
  }, [token]);

  function handleSelect(note: api.Note) {
    setSelectedId(note.id);
    setTitle(note.title);
    setContent(note.content);
    setError(null);
  }

  function handleNew() {
    setSelectedId(null);
    setTitle("");
    setContent("");
    setError(null);
  }

  async function handleSave(e: FormEvent) {
    e.preventDefault();
    if (!token) return;
    setSaving(true);
    setError(null);
    try {
      if (selectedId === null) {
        const created = await api.createNote(token, title, content);
        setNotes((prev) => [created, ...prev]);
        setSelectedId(created.id);
      } else {
        const updated = await api.updateNote(token, selectedId, { title, content });
        setNotes((prev) => prev.map((n) => (n.id === updated.id ? updated : n)));
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to save note.");
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(id: number) {
    if (!token) return;
    if (!window.confirm("Delete this note? This can't be undone.")) return;
    try {
      await api.deleteNote(token, id);
      setNotes((prev) => prev.filter((n) => n.id !== id));
      if (selectedId === id) handleNew();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to delete note.");
    }
  }

  if (loading) return <p className="notes-status">Loading notes...</p>;

  return (
    <div className="notes-layout">
      <aside className="notes-sidebar">
        <button className="new-note-btn" onClick={handleNew}>
          + New note
        </button>
        {notes.length === 0 && <p className="notes-empty">No notes yet.</p>}
        <ul className="notes-list">
          {notes.map((note) => (
            <li key={note.id}>
              <button
                className={`notes-list-item ${note.id === selectedId ? "active" : ""}`}
                onClick={() => handleSelect(note)}
              >
                {note.title || "Untitled"}
              </button>
            </li>
          ))}
        </ul>
      </aside>
      <section className="notes-editor">
        <form onSubmit={handleSave}>
          <input
            className="notes-title-input"
            placeholder="Title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
          <textarea
            className="notes-content-input"
            placeholder="Write something..."
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows={14}
            required
          />
          {error && <p className="auth-error">{error}</p>}
          <div className="notes-actions">
            <button type="submit" disabled={saving}>
              {saving ? "Saving..." : "Save"}
            </button>
            {selectedId !== null && (
              <button type="button" className="delete-btn" onClick={() => handleDelete(selectedId)}>
                Delete
              </button>
            )}
          </div>
        </form>
      </section>
    </div>
  );
}