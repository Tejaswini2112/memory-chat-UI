import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

# --- API Config ---
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.environ["GROQ_API_KEY"]
GROQ_MODEL = "llama-3.1-8b-instant"

GROQ_EXTRACT_MODEL = "llama-3.1-8b-instant"

SYSTEM_PROMPT = """You are a friendly and helpful assistant called Buddy.
You remember important facts about the user from past conversations.
Keep your replies concise and warm.

FORMATTING RULES (follow strictly):
- Structure every response clearly using **sections with emoji headers** (e.g. 🚀 Phase 1: Title, 📊 Key Concepts, ✅ Summary).
- Use blank lines between sections for readability.
- Use bullet points (•) for individual items within a section. Each bullet must be on its own line.
- When explaining a process, roadmap, or multi-step topic, break it into **numbered phases or stages** with clear titles.
- Keep each bullet point short and scannable — one idea per bullet.
- Add a brief intro line before the structured content (1 sentence max).
- For simple/short answers, you don't need phases — just use clear bullets and headers where helpful.
- Never dump everything into a single flat list. Group related points under meaningful headers.
- Use bold (**text**) to highlight key terms or names within bullets."""

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "..", "smart_memory.json")

# --- State ---
# sessions[session_id] = [{"role": ..., "content": ...}, ...]
sessions: dict[str, list[dict]] = {}

# memory_store[session_id] = ["fact1", "fact2", ...]
memory_store: dict[str, list[str]] = {}


# --- Persistence ---
def _load_memory():
    global memory_store
    try:
        with open(MEMORY_FILE, "r") as f:
            memory_store = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        memory_store = {}


def _save_memory():
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory_store, f, indent=2)


# Load on startup
_load_memory()


# --- Smart Memory ---
def extract_memory(user_message: str) -> str | None:
    """Use Groq to decide if the user message contains an important fact worth remembering."""
    prompt = f"""Analyze this user message and decide if it contains any important personal information worth remembering (like their name, age, job, preferences, goals, location, hobbies, or meaningful facts about them).

If YES — respond with ONLY a single short fact sentence (e.g. "User's name is Alex" or "User prefers dark mode").
If NO — respond with exactly the word "NONE".

User message: "{user_message}"
"""
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_EXTRACT_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
    }

    try:
        resp = requests.post(GROQ_URL, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        result = data["choices"][0]["message"]["content"].strip()
        if result.upper() == "NONE":
            return None
        return result
    except Exception as e:
        print(f"[extract_memory] Groq call failed: {e}")
        return None


def build_memory_context(session_id: str) -> str:
    """Format saved facts into a block for the system prompt."""
    facts = memory_store.get(session_id, [])
    if not facts:
        return ""
    facts_text = "\n".join(f"- {fact}" for fact in facts)
    return f"\n\nHere are important things you remember about this user:\n{facts_text}\n\nUse these facts naturally in conversation when relevant."


# --- Chat ---
def chat(session_id: str, user_message: str) -> dict:
    # Init session if new
    if session_id not in sessions:
        sessions[session_id] = []
    if session_id not in memory_store:
        memory_store[session_id] = []

    history = sessions[session_id]
    history.append({"role": "user", "content": user_message})

    # Build system prompt with memory context
    memory_context = build_memory_context(session_id)
    system_prompt = SYSTEM_PROMPT + memory_context

    messages = [{"role": "system", "content": system_prompt}] + history

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
    }

    response = requests.post(GROQ_URL, json=payload, headers=headers)
    response.raise_for_status()

    data = response.json()
    reply = data["choices"][0]["message"]["content"].strip()
    history.append({"role": "assistant", "content": reply})

    # Extract memory from the user message
    new_fact = extract_memory(user_message)
    new_fact_saved = False

    if new_fact and new_fact not in memory_store[session_id]:
        memory_store[session_id].append(new_fact)
        _save_memory()
        new_fact_saved = True

    return {
        "reply": reply,
        "memory": memory_store[session_id],
        "new_fact_saved": new_fact_saved,
    }


def clear_session(session_id: str):
    """Wipe both conversation history and saved memory for a session."""
    sessions.pop(session_id, None)
    if session_id in memory_store:
        del memory_store[session_id]
        _save_memory()


def get_memory(session_id: str) -> list[str]:
    return memory_store.get(session_id, [])
