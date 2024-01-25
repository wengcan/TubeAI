import os,subprocess
from src.utils import data_path
class YouTube:
    def __init__(self):
        os.makedirs(data_path, exist_ok=True)
    async def download(self, folder:str, video_url: str):
        try:
            output_path = os.path.join(data_path, folder, '%(title)s.%(ext)s')
            command = ['yt-dlp', '-f', 'worst', '--skip-download', '--write-auto-subs', '--sub-format', 'vtt', '-o', output_path, video_url]
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = process.communicate()
        except Exception as e:
            print(e)