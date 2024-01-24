import os,subprocess
class YouTube:
    def __init__(self):
        self.download_folder = os.path.join(os.path.abspath(os.curdir), 'data')
        os.makedirs(self.download_folder, exist_ok=True)
    async def download(self,video_url):
        try:
            output_path = os.path.join(self.download_folder, 'downloaded_video.%(ext)s')
            output_path = os.path.join(self.download_folder, '%(title)s.%(ext)s')
            command = ['yt-dlp', '-f', 'worst', '--skip-download', '--write-auto-subs', '--sub-format', 'vtt', '-o', output_path, video_url]
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = process.communicate()
            print(output)
        except Exception as e:
            print(e)