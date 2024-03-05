from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.responses import PlainTextResponse,StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from .proxy import Proxy

load_dotenv()


proxy = Proxy()
app = FastAPI()
origins = [
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




class Chat(BaseModel):
    content: str


name_list = ["summarize"]
def check_name(name: str):
    if name in name_list:
        return name
    else:
        raise HTTPException(status_code=404, detail=f"Name '{name}' not found in the list.")


@app.get("/ping",response_class=PlainTextResponse)
def read_root():
    return "pong"

@app.post("/chat")
async def chat(chat: Chat):
    return StreamingResponse(proxy.chat(chat.content))

@app.get("/load")
async def load(url: str):
    return await proxy.get_video_info(url = url)


@app.get("/shortcut/{name}")
async def shortcut(url: str, name: str = Depends(check_name)):
    return await proxy.run_shortcut(url = url, name="summarize")
