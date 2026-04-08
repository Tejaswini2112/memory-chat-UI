from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from chatapi.memory_chatbot import chat, history

app = FastAPI()

# Allow CORS for the frontend (running on port 3000 usually)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str


@app.get("/api/greet")
async def greet():
    return {"message": "Hello from FastAPI!"}

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        # Call the existing chat function from our chatbot module
        reply = chat(request.message)
        return {"reply": reply, "history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/clear")
async def clear_memory():
    # Clear the global history list
    history.clear()
    return {"status": "success", "message": "Memory cleared"}

@app.get("/api/memory")
async def get_memory():
    # Retrieve the current conversation history
    return {"history": history}
