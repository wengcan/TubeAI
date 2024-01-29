import os
import google.generativeai as genai
from src.utils import safety_settings
class Gemini:
    def __init__(self):
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel('gemini-pro', safety_settings= safety_settings)
    def generate_content(self, content: str):
        if content != "":
            response = self.model.generate_content(content, stream=True)
            return response

