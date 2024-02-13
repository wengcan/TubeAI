import asyncio
import importlib,os,uuid
from enum import Enum
from socketio import AsyncServer
from .utils import file_exist, extract_video_id, data_path, get_video_folder_path, get_vtt, get_info
from typing import Dict
class Command(Enum):
    LOAD = "load"
    QA = "qa"
    CHAT = "chat"
    SHORTCUT = "shortcut"
class ResultKey(Enum):
    INFO = "info"

class OutBoundMessageStatus(Enum):
    ACCEPTED = "a"
    GENERATING = "g"
    FINISHED = "f"
    ERROR = "e"


class Proxy:
    __classes = {}
    __sio: AsyncServer = None
    def __init__(self, sio) -> None:
        self.__sio = sio
        for module_name in os.listdir(os.path.join(os.path.abspath(os.curdir), 'src', 'app')):
            module = importlib.import_module(f"src.app.{module_name}")
            for name in dir(module):
                obj = getattr(module, name)
                if hasattr(obj, "__module__") and obj.__module__ == f"src.app.{module_name}" and hasattr(obj, "__class__"):
                    self.__classes[module_name] = obj()
    async def chat(self,sid: str,  message_id: str, message_content: str):
        response = self.__classes.get('gemini').generate_content(message_content)
        for chunk in response:
            #print(chunk.text)
            await self.__sio.emit('chat', {"id":message_id,"content":chunk.text} , room=sid)

    async def __download(self, url: str):
        video_id = extract_video_id(url=url)
        if video_id is not None:
            folder_path =  get_video_folder_path(video_id=video_id)
            if file_exist(folder_path) is not True:       
                await self.__classes.get('youtube').download(folder_path, url)
        return video_id
    async def __video_info(self, video_id):
        folder_path =  get_video_folder_path(video_id=video_id)
        return await get_info(folder_path=folder_path)


    async def __summarize(self, video_id: str):
        folder = os.path.join(data_path, 'youtube', video_id)
        if self.__classes.get('langchain').id_exist(video_id) is not True: 
            vtt_contents = await get_vtt(folder)
            return self.__classes.get('langchain').add_documents(id_key=video_id,text=vtt_contents)

    async def __run_shortcut(self, id: str, name: str):
        if name == "summarize":
           return  await self.__summarize(id)
    async def __emit(self, event: str, data: Dict, room: str):
        await self.__sio.emit(event, data , room=room)
        await asyncio.sleep(0.0001)
        
    async def handle_message(self,sid: str, message: dict):
        try:
            message_id = uuid.uuid4()
            cmd = message.get("cmd")
            if cmd == Command.LOAD.value:
                url = message.get("content")
                video_id = await self.__download(url=url)
                info = await self.__video_info(video_id=video_id)
                if info is not None:
                    title, thumbnail, description = info
                await self.__sio.emit('result', {
                    "id":f'{message_id}', 
                    "key": ResultKey.INFO.value,
                    "data": {
                        'url': url, 
                        'video_id':  video_id, 
                        'title' :title,
                        'thumbnail': thumbnail,
                        'description': description
                    }
                } , room=sid)
            elif cmd == Command.SHORTCUT.value:
                id = message.get("id")
                name = message.get("name")
                await self.__emit('message', {
                    "id": f'{message_id}', 
                    'status': OutBoundMessageStatus.ACCEPTED.value
                } , room=sid)
                resp_content = await self.__run_shortcut(id, name)
                for content in resp_content:
                    await self.__emit('message', {
                        "id": f'{message_id}',
                        "content": content, 
                        'status': OutBoundMessageStatus.GENERATING.value
                    } , room=sid)
                await self.__emit('message', {
                    "id": f'{message_id}',
                    'status': OutBoundMessageStatus.FINISHED.value
                } , room=sid)
                
            elif cmd ==  Command.CHAT.value:
                await self.__emit('message', {
                    "id": f'{message_id}', 
                    'status': OutBoundMessageStatus.ACCEPTED.value
                } , room=sid)

                
                response = self.__classes.get('gemini').generate_content(message.get("content"))
   
                if 'candidates' in response:
                    for candidate in response.candidates:
                        await self.__emit('message', {
                            "id":f'{message_id}',
                            "content": "".join([part.text for part in candidate.content.parts]), 
                            'status': OutBoundMessageStatus.GENERATING.value
                        } , room=sid)
                else:
                    for chunk in response:
                        await self.__emit('message', {
                            "id":f'{message_id}',
                            "content":chunk.text, 
                            'status': OutBoundMessageStatus.GENERATING.value
                        } , room=sid)
                await self.__emit('message', {
                    "id": f'{message_id}',
                    'status': OutBoundMessageStatus.FINISHED.value
                } , room=sid)
            pass
        except Exception as e:
            print(e)             

