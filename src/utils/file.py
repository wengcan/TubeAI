import asyncio
import io,os,json
import webvtt
import aiofiles
from  typing import Tuple

env_path = os.getenv('DATA_PATH')
data_path = os.path.join(os.path.abspath(os.curdir), 'data') if env_path is None else env_path
chromadb_path = os.path.join(data_path, 'chromadb')
def file_exist(filename: str):
    return os.path.exists(filename)

def get_video_folder_path(video_id: str) -> str:
    return os.path.join(data_path, 'youtube', video_id)

async def get_file_contents(file_path: str ):
    async with aiofiles.open(file_path, mode='r') as file:
        contents = await file.read()
        return contents

async def get_file_with_ext(folder_path: str, file_ext: str, sleeptime: int = 10) -> str | None:
    retry_times= 0
    while not file_exist(folder_path):
        if retry_times > 10:
            return None
        retry_times += 1
        await asyncio.sleep(sleeptime)    
    files = os.listdir(folder_path)
    ext_files = [file for file in files if file.lower().endswith(f'.{file_ext}')]
    if len(ext_files) > 0:
        return os.path.join(folder_path, ext_files[0])
    else:
        return None
def convert_vtt(filepath: str):
    vtt = webvtt.read(filepath)
    transcript = ""
    lines = []
    for line in vtt:
        lines.extend(line.text.strip().splitlines())
    previous = None
    for line in lines:
        if line == previous:
            continue
        transcript += " " + line
        previous = line
    return transcript

async def get_vtt(folder_path: str) -> str:
    file_path = await get_file_with_ext(folder_path=folder_path ,  file_ext= "vtt")
    return convert_vtt(filepath=file_path) if file_path else ""
async def get_info(folder_path: str) -> Tuple[str] | None:
    file_path = await get_file_with_ext(folder_path=folder_path , file_ext= "json")
    if file_path:
        contents = await get_file_contents(file_path= file_path)
        data = json.loads(contents)
        return (data["title"], data["thumbnail"], data["description"])
    return None