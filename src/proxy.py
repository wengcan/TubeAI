import importlib,os,uuid
from enum import Enum
from socketio import AsyncServer
from .utils import file_exist, extract_video_id, data_path,get_vtt_file

class Command(Enum):
    LOAD = "load"
    QA = "qa"
    SUMMARY = "summary"
    CHAT = "chat"


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
        folder = os.path.join(data_path, 'youtube', video_id)
        if video_id is not None:
            if file_exist(folder) is not True:       
                await self.__classes.get('youtube').download(folder, url)

    async def __summary(self, video_id: str):
        folder = os.path.join(data_path, 'youtube', video_id)
        if self.__classes.get('langchain').id_exist(video_id) is not True: 
            vtt_contents = await get_vtt_file(folder)
            self.__classes.get('langchain').add_documents(id_key=video_id,text=vtt_contents)
    async def handle_message(self,sid: str, message: dict):
        try:
            message_id = uuid.uuid4()
            cmd = message.get("cmd")
            await self.__sio.emit('message', {"id": f'{message_id}'} , room=sid)
            if cmd == Command.LOAD.value:
                url = message.get("content")
                video_id = await self.__download(url=url)
                await self.__sio.emit('result', {"id":f'{message_id}', 'url': url, 'video_id':  video_id} , room=sid)
            elif cmd == Command.SUMMARY.value:
                video_id = message.get("video_id")
                result = self.__classes.get('langchain').query_documents(f'{video_id}/summaries')
                pass
            elif cmd ==  Command.CHAT.value:
                response = self.__classes.get('gemini').generate_content(message.get("content"))
                for chunk in response:
                    print(chunk.text)
                    await self.__sio.emit('message', {"id":f'{message_id}',"content":chunk.text} , room=sid)
            pass
        except Exception as e:
            print(e)             

