import asyncio
import socketio
import json

sio = socketio.AsyncClient()

@sio.event
async def connect():
    print('connection established')

@sio.event
async def my_message(data):
    print('message received with ', data)
    await sio.emit('my response', {'response': 'my response'})

@sio.event
async def disconnect():
    print('disconnected from server')

async def main():
    await sio.connect('http://localhost:8080')
    #await sio.wait()
    await sio.emit('download', json.dumps({'id': '1234', 'url': 'https://www.youtube.com/watch?v=fx3ILcSV7a0&t=2s'}))

if __name__ == '__main__':
    asyncio.run(main())