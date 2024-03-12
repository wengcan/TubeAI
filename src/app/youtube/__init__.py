from typing import Dict
import os,subprocess

class YouTube:
    def __init__(self, config: Dict[str, str]):
        os.makedirs(config.get("data_path") , exist_ok=True)
    async def download(self, folder:str, video_url: str):
        try:
            output_path = os.path.join(folder, '%(title)s.%(ext)s')
            command = [
                'yt-dlp', 
                '-f', 
                'worst', 
                '--skip-download', 
                '--write-auto-subs', 
                '--write-info-json', 
                '--sub-format', 
                'vtt', 
                '-o',
                output_path, 
                video_url
            ]
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = process.communicate()
        except Exception as e:
            print(e)