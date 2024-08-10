from fastapi import FastAPI, Request, WebSocket, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from chat_processor import ChatProcessor
import os
import secrets

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Read the API key, username, and password from environment variables
api_key = os.environ.get("ANTHROPIC_API_KEY")
USERNAME = os.environ.get("CHAT_USERNAME")
PASSWORD = os.environ.get("CHAT_PASSWORD")

if api_key is None:
    raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
if USERNAME is None:
    raise ValueError("CHAT_USERNAME environment variable is not set")
if PASSWORD is None:
    raise ValueError("CHAT_PASSWORD environment variable is not set")

# Initialize with API key
chat_processor = ChatProcessor(api_key)

# Use pydantic to ensure that incoming chat messages are strings
class ChatMessage(BaseModel):
    message: str

# Contains entirety of chat history, across different sessions, until cleared or the server is restarted
chat_history = []

# Set up HTTP Basic Auth
security = HTTPBasic()

# Authenticate the user
def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, USERNAME)
    correct_password = secrets.compare_digest(credentials.password, PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Render the UI homepage
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, username: str = Depends(authenticate)):
    return templates.TemplateResponse("index.html", {"request": request})

# Websocket for the UI chat interface
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        chat_message = ChatMessage(message=data)

        # Use the ChatProcessor to generate a response
        recent_history = chat_history[-10:] if len(chat_history) > 10 else chat_history
        response = chat_processor.process_message(chat_message.message, recent_history)

        chat_history.append({"user": chat_message.message, "bot": response})
        await websocket.send_json({"user": chat_message.message, "bot": response})

# A /chat endpoint is also added, in addition to the websocket which handles the UI chat, to allow for programmatic access to the chat functionality.
@app.post("/chat")
async def chat_endpoint(chat_message: ChatMessage, username: str = Depends(authenticate)):
    global chat_history

    # Get recent history (up to last 10 messages)
    recent_history = chat_history[-10:] if len(chat_history) > 10 else chat_history

    # Process message with context
    response = chat_processor.process_message(chat_message.message, recent_history)

    # Update chat history
    chat_history.append({"user": chat_message.message, "bot": response})

    return {"response": response}

# Return the chat history
@app.get("/chat_history")
async def get_chat_history(username: str = Depends(authenticate)):
    return chat_history

# Clear chat history
@app.post("/clear_chat")
async def clear_chat(username: str = Depends(authenticate)):
    global chat_history
    chat_history = []
    return {"status": "success"}
