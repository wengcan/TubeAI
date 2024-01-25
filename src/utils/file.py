import asyncio
import io,os
import webvtt
import aiofiles

env_path = os.getenv('DATA_PATH')
data_path = os.path.join(os.path.abspath(os.curdir), 'data') if env_path is None else env_path
def file_exist(filename: str):
    return os.path.exists(filename)

async def get_file_contents(filename: str ):
    # while not file_exist(filename):
    #     await asyncio.sleep(sleeptime)
    async with aiofiles.open(filename, mode='r') as file:
        contents = await file.read()
        return contents

async def get_vtt_file(folder_path: str, sleeptime: int = 10):
    while not file_exist(folder_path):
        await asyncio.sleep(sleeptime)    
    files = os.listdir(folder_path)
    vtt_files = [file for file in files if file.lower().endswith('.vtt')]  
    if len(vtt_files) > 0:
        contents = convert_vtt(os.path.join(folder_path, vtt_files[0]))
        return contents
    else:
        return ""


def convert_vtt(filename: str):
    vtt = webvtt.read(filename)
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
