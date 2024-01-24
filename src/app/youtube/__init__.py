import os,subprocess
from src.utils import data_path
class YouTube:
    def __init__(self):
        os.makedirs(data_path, exist_ok=True)
    async def download(self, video_id, video_url):
        try:
            output_path = os.path.join(data_path, video_id, '%(title)s.%(ext)s')
            command = ['yt-dlp', '-f', 'worst', '--skip-download', '--write-auto-subs', '--sub-format', 'vtt', '-o', output_path, video_url]
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = process.communicate()
            print(output)
            return output_path
        except Exception as e:
            print(e)