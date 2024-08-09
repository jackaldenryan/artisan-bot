from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ChatMessage(BaseModel):
    message: str

@app.post("/chat")
async def chat(chat_message: ChatMessage):
    n = len(chat_message.message)
    response = f"You said: {chat_message.message}. And this message has {n} chars."
    return {"response": response}