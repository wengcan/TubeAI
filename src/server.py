from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl, validator
from dotenv import load_dotenv
from fastapi.responses import PlainTextResponse,StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from .proxy import Proxy
from .config import languages, shortcut_keys

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
    
class BaseRequest(BaseModel):
    url: HttpUrl
    lang: str = "en" 
    @validator("lang")
    def validate_lang(cls, v):
        valid_langs = languages.keys()
        if v not in valid_langs:
            raise ValueError("Invalid language code")
        return v    
class QARequest(BaseRequest):
    question: str = None

def check_name(name: str):
    if name in shortcut_keys:
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
async def load(load_request: BaseRequest):
    return await proxy.get_video_info(url = str(load_request.url))


@app.post("/shortcut/{name}")
async def shortcut(
    request: BaseRequest,
    name: str = Depends(check_name),
):
    resp = proxy.run_shortcut(url = str(request.url), name=name, lang= languages[request.lang])
    return StreamingResponse(resp)

# @app.post("/qa")
# async def shortcut(
#     request: QARequest
# ):
#     return await proxy.run_qa(
#         url=str(request.url), 
#         question= request.question
#     )