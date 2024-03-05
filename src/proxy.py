import asyncio
import importlib,os,uuid
from enum import Enum
from .utils import file_exist, extract_video_id, data_path, get_video_folder_path, get_vtt, get_info
from pydantic import BaseModel
from typing import Dict


class VideoInfo(BaseModel):
    title: str
    thumbnail: str
    description: str
    def __init__(self, data):
        super().__init__(
            title=data[0],
            thumbnail=data[1],
            description=data[2]
    )

class Proxy:
    __classes = {}
    def __init__(self) -> None:
        for module_name in os.listdir(os.path.join(os.path.abspath(os.curdir), 'src', 'app')):
            module = importlib.import_module(f"src.app.{module_name}")
            for name in dir(module):
                obj = getattr(module, name)
                if hasattr(obj, "__module__") and obj.__module__ == f"src.app.{module_name}" and hasattr(obj, "__class__"):
                    self.__classes[module_name] = obj()
    async def chat(self, message_content: str):
        response = self.__classes.get('gemini').generate_content(message_content)
        for chunk in response:
            await asyncio.sleep(0.001)
            yield chunk.text
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


    async def __summarize_youtube(self, video_id: str):
        folder = os.path.join(data_path, 'youtube', video_id)
        if self.__classes.get('langchain').id_exist(video_id) is not True: 
            vtt_contents = await get_vtt(folder)
            return self.__classes.get('langchain').add_documents(id_key=video_id,text=vtt_contents)

    async def run_shortcut(self, url: str, name: str):
        video_id = extract_video_id(url=url)
        if name == "summarize":
           return  await self.__summarize_youtube(video_id)
        
    async def get_video_info(self, url: str) -> VideoInfo:
        video_id = await self.__download(url=url)
        info = await self.__video_info(video_id=video_id)
        return VideoInfo(info)
