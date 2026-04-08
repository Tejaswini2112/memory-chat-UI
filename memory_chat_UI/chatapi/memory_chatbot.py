import os
import requests
from dotenv import load_dotenv

load_dotenv()

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.environ["GROQ_API_KEY"]
GROQ_MODEL = "llama-3.1-8b-instant"

SYSTEM_PROMPT = """You are a friendly and helpful assistant called Buddy.
You remember everything said earlier in the conversation.
Keep your replies concise and warm."""

# This list is our "memory" — it starts empty and grows each turn
history = []


def chat(user_message: str) -> str:
    global history

    history.append({"role": "user", "content": user_message})

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history

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
    return reply


def main():
    print("Buddy is ready! Type 'quit' to exit, 'clear' to reset memory.\n")
    print("-" * 50)

    while True:
        user_input = input("\nYou: ").strip()
        if not user_input:
            continue
        if user_input.lower() == "quit":
            print("Goodbye!")
            break
        if user_input.lower() == "clear":
            history.clear()
            print("(Memory cleared — starting fresh)")
            continue
        if user_input.lower() == "history":
            print(f"(Memory has {len(history)} messages so far)")
            continue
        try:
            reply = chat(user_input)
            print(f"\nBuddy: {reply}")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
