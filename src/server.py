from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from dotenv import load_dotenv
from fastapi.responses import PlainTextResponse,StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from .proxy import Proxy
from .proxy import shortcuts

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
    
class LoadRequest(BaseModel):
    url: HttpUrl
class ShortcutRequest(LoadRequest):
    question: str = None

    
name_list = list(shortcuts.keys())

print(name_list)
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

@app.post("/load")
async def load(load_request: LoadRequest):
    return await proxy.get_video_info(url = str(load_request.url))


@app.post("/shortcut/{name}")
async def shortcut(
    short_request: ShortcutRequest,
    name: str = Depends(check_name),
):
    if name in ["summarize", "keywords", "comments"]:
        return await proxy.run_shortcut(url = str(short_request.url), name=name)
    elif name == "qa":
        return await proxy.run_shortcut(url=str(short_request.url), name="qa", question= short_request.question)
