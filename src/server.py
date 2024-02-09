import asyncio
import json,socketio
from dotenv import load_dotenv
from .proxy import Proxy

load_dotenv()


sio = socketio.AsyncServer(logger=True, engineio_logger=True , cors_allowed_origins='*', async_mode='asgi', compress=True)



app = socketio.ASGIApp(sio)


proxy = Proxy(sio)

@sio.event
def connect(sid, environ):
    print("connect ", sid)

@sio.event
async def message(sid, data):
    loop = asyncio.get_event_loop()
    try:
        await loop.create_task(proxy.handle_message(sid= sid, message=json.loads(data)))
        #await sio.emit('response', f"Received your message: {data}", room=sid)
    except Exception as e:
        print(e)


@sio.event
def disconnect(sid):
    print('disconnect ', sid)

