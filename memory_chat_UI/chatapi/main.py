from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from chatapi.memory_chatbot import chat, clear_session, get_memory

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


@app.get("/api/greet")
async def greet():
    return {"message": "Hello from FastAPI!"}


@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        result = chat(request.session_id, request.message)
        return {
            "reply": result["reply"],
            "memory": result["memory"],
            "new_fact_saved": result["new_fact_saved"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/memory/{session_id}")
async def get_memory_endpoint(session_id: str):
    return {"memory": get_memory(session_id)}


@app.delete("/api/clear/{session_id}")
async def clear_endpoint(session_id: str):
    clear_session(session_id)
    return {"status": "success", "message": f"Session '{session_id}' cleared"}
