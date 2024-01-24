import os
import google.generativeai as genai
class Gemini:
    def __init__(self):
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel('gemini-pro')
    def generate_content(self, content: str):
        if content != "":
            response = self.model.generate_content(content, stream=True)
            return response

