# Memory Chatbot — AI Learning Project

A chatbot with memory capabilities built with **Next.js** (frontend) and **FastAPI** (backend), powered by **Groq LLaMA 3.1**.

---

## Version History

### v1 — Basic Memory Chatbot (Initial Commit)

A simple conversational chatbot with in-session memory.

**Features:**
- Single global conversation history stored in a Python list
- FastAPI backend with `/api/chat`, `/api/clear`, and `/api/memory` endpoints
- Next.js frontend with a chat UI and memory sidebar
- Hardcoded bot responses for memory acknowledgment
- Plain text message rendering
- CLI mode support (`memory_chatbot.py` runnable standalone)

**How it worked:**
- All messages were appended to a global `history` list
- The full history was sent to Groq on each request for context
- Memory sidebar showed truncated snippets of user messages (client-side only)
- Clearing memory wiped the in-memory list (lost on server restart)

---

### v2 — Smart Persistent Memory (Current)

A major upgrade introducing **AI-powered memory extraction** and **persistent storage**.

**New Features:**
- **Smart memory extraction** — a second LLM call analyzes each user message to extract important personal facts (name, preferences, goals, etc.)
- **Persistent memory** — facts are saved to `smart_memory.json` and survive server restarts
- **Session support** — multiple independent sessions via `session_id` parameter
- **Markdown rendering** — bot responses render rich markdown (headers, bold, bullets, emoji) using `react-markdown` with Tailwind Typography
- **Structured responses** — system prompt updated to produce well-formatted responses with sections, emoji headers, and bullet points
- **Real memory sidebar** — sidebar now shows actual extracted facts from the backend, not client-side snippets

**Backend changes:**
- `memory_chatbot.py` — added `extract_memory()`, `build_memory_context()`, session/memory stores, JSON persistence
- `main.py` — session-aware endpoints: `POST /api/chat`, `GET /api/memory/{session_id}`, `DELETE /api/clear/{session_id}`

**Frontend changes:**
- `message-bubble.tsx` — added `ReactMarkdown` rendering for bot messages with prose styling
- `chat-interface.tsx` — memory sidebar driven by backend facts; clear calls `DELETE` endpoint
- Added `react-markdown` and `@tailwindcss/typography` dependencies

---

## Tech Stack

| Layer    | Technology                  |
|----------|-----------------------------|
| Frontend | Next.js, React, Tailwind CSS, shadcn/ui |
| Backend  | FastAPI, Python             |
| LLM      | Groq API (LLaMA 3.1 8B Instant) |
| Memory   | JSON file persistence       |

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.11+
- Groq API key

### Backend
```bash
cd memory_chat_UI/chatapi
pip install -r requirements.txt
# Create .env with GROQ_API_KEY=your_key
uvicorn main:app --reload
```

### Frontend
```bash
cd memory_chat_UI
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to use the chatbot.
