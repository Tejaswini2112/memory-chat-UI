import os
import json
import math
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


def search_memories(query: str, facts: list[str], top_k: int = 5) -> list[str]:
    """Score each fact against the query using TF-IDF-style keyword overlap and
    return the top_k most relevant facts.

    How the scoring works:
    1. Tokenize the query and every fact into lowercase words (letters/digits only).
    2. Build a document-frequency (DF) table: for each word, how many facts contain it.
    3. For every fact, compute a relevance score against the query:
       - For each query word that appears in the fact, add its IDF weight.
       - IDF = log(N / DF) where N = total number of facts.  Rare words score higher
         than common ones, so "piano" beats "the" when matching "I play piano".
    4. Sort facts by descending score and return the top_k.
    5. If every fact scored 0 (no keyword overlap at all), fall back to the most
       recent 5 facts by list index so the bot still has some context.
    """
    if not facts:
        return []

    # --- tokenizer: split on non-alphanumeric chars, lowercase ---
    def _tokenize(text: str) -> set[str]:
        tokens: set[str] = set()
        word = []
        for ch in text.lower():
            if ch.isalnum():
                word.append(ch)
            else:
                if word:
                    tokens.add("".join(word))
                    word = []
        if word:
            tokens.add("".join(word))
        return tokens

    query_tokens = _tokenize(query)
    if not query_tokens:
        # No usable words in the query — return the most recent facts
        return facts[-top_k:]

    # Tokenize every fact once
    fact_tokens = [_tokenize(f) for f in facts]

    # --- Document frequency: how many facts contain each word ---
    n = len(facts)
    df: dict[str, int] = {}
    for tokens in fact_tokens:
        for word in tokens:
            df[word] = df.get(word, 0) + 1

    # --- Score each fact against the query using IDF-weighted overlap ---
    # score(fact) = sum of idf(w) for every query word w that appears in fact
    # idf(w) = log(N / df(w))  — words in fewer facts get a higher weight
    scores: list[float] = []
    for tokens in fact_tokens:
        score = 0.0
        for qw in query_tokens:
            if qw in tokens and qw in df:
                score += math.log(n / df[qw])
        scores.append(score)

    # --- Pick the top_k highest-scoring facts ---
    indexed = sorted(enumerate(scores), key=lambda pair: pair[1], reverse=True)
    top = [facts[i] for i, s in indexed[:top_k] if s > 0]

    # Fallback: if nothing matched at all, return the last top_k facts (most recent)
    if not top:
        return facts[-top_k:]

    return top


def build_memory_context(session_id: str, user_message: str = "") -> str:
    """Format the most relevant saved facts into a block for the system prompt.

    Uses search_memories() to pick only the facts that match the current query
    instead of dumping every fact into the prompt.
    """
    facts = memory_store.get(session_id, [])
    if not facts:
        return ""
    # Retrieve the most relevant facts for this particular message
    relevant = search_memories(user_message, facts) if user_message else facts[-5:]
    facts_text = "\n".join(f"- {fact}" for fact in relevant)
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

    # Build system prompt with only the most relevant memories for this message
    memory_context = build_memory_context(session_id, user_message)
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
