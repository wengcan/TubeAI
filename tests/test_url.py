import unittest
from app.langchain import extract_video_id

class TestURL(unittest.TestCase):
    def test_youtube_url(self):
        self.assertEqual(extract_video_id("https://www.youtube.com/watch?v=fx3ILcSV7a0&t=2s"), "fx3ILcSV7a0")

if __name__ == '__main__':
    unittest.main()