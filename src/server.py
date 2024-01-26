import asyncio
import json,socketio
from dotenv import load_dotenv
from .proxy import Proxy

load_dotenv()


sio = socketio.AsyncServer(cors_allowed_origins='*', async_mode='asgi', compress=True)
app = socketio.ASGIApp(sio)


proxy = Proxy(sio)

@sio.event
def connect(sid, environ):
    print("connect ", sid)

@sio.event
async def message(sid, data):
    await sio.emit('response', f"Received your message: {data}", room=sid)


@sio.event
async def download(sid, data)
    try:
        message = json.loads(data)    
        await asyncio.create_task(proxy.download(sid,message["id"],message["url"]))
    except Exception as e:
        print(e)        
@sio.event
async def qa(sid, data):
    try:
        message = json.loads(data)    
        await asyncio.create_task(proxy.qa(sid,message["id"],  message["url"]))
    except Exception as e:
        print(e)   

@sio.event
async def chat(sid, data):
    try:
        message = json.loads(data)
        await asyncio.create_task(proxy.chat(sid,message["id"], message["content"]))
    except Exception as e:
        print(e)

@sio.event
def disconnect(sid):
    print('disconnect ', sid)

