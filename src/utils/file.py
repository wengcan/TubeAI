import asyncio
import io,os
import webvtt
from aiofiles import os as aioos

env_path = os.getenv('DATA_PATH')
data_path = os.path.join(os.path.abspath(os.curdir), 'data') if env_path is None else env_path
def file_exist(filename: str):
    return os.path.exists(filename)

async def get_file_contents(filename: str, sleeptime: int = 10):
    while not file_exist(filename):
        await asyncio.sleep(sleeptime)
    async with aioos.open(filename, 'r') as file:
        contents = await file.read()
        return contents
async def convert_vtt(filename: str):
    contents = await get_file_contents(filename=filename)
    buffer = io.StringIO(contents)
    vtt = webvtt.read_buffer(buffer.read())
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
