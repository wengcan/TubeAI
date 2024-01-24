import re

def extract_video_id(url):
    pattern = re.compile(r'(https?://)?(www\.)?youtube\.(com|be)/.+[=/](.{11})')
    match = pattern.match(url)
    if match:
        video_id = match.group(4)
        return video_id
    else:
        return None