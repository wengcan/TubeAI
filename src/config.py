import os
from enum import Enum
from pydantic import BaseModel


env_path = os.getenv('DATA_PATH')
data_path = os.path.join(os.path.abspath(os.curdir), 'data') if env_path is None else env_path
chromadb_path = os.path.join(data_path, 'chromadb')


languages = {
  "ar": "Arabic",
  "bn": "Bengali",
  "bg": "Bulgarian",
  "zh": "Chinese",
  "hr": "Croatian",
  "cs": "Czech",
  "da": "Danish",
  "nl": "Dutch",
  "en": "English",
  "et": "Estonian",
  "fi": "Finnish",
  "fr": "French",
  "de": "German",
  "el": "Greek",
  "iw": "Hebrew",
  "hi": "Hindi",
  "hu": "Hungarian",
  "id": "Indonesian",
  "it": "Italian",
  "ja": "Japanese",
  "ko": "Korean",
  "lv": "Latvian",
  "lt": "Lithuanian",
  "no": "Norwegian",
  "pl": "Polish",
  "pt": "Portuguese",
  "ro": "Romanian",
  "ru": "Russian",
  "sr": "Serbian",
  "sk": "Slovak",
  "sl": "Slovenian",
  "es": "Spanish",
  "sw": "Swahili",
  "sv": "Swedish",
  "th": "Thai",
  "tr": "Turkish",
  "uk": "Ukrainian",
  "vi": "Vietnamese"
}
languages_list = languages.keys()


class Property(BaseModel):
    prompt: str
    refine_prompt: str

class Shortcut(BaseModel):
    summarize: Property
    keywords: Property
    comments: Property

shortcut_data = {
    "summarize": {
        "prompt": """Write a concise summary of the following:
        {doc}
        CONCISE SUMMARY:""",
        "refine_prompt": (
            "Your job is to produce a final summary\n"
            "We have provided an existing summary up to a certain point: {existing_answer}\n"
            "We have the opportunity to refine the existing summary"
            "(only if needed) with some more context below.\n"
            "------------\n"
            "{text}\n"
            "------------\n"
            "Given the new context, refine the original summary in  {lang}"
            "If the context isn't useful, return the original summary in {lang}."
            "Output the summary directly, do not add any prefixes"
        )
    },
    "keywords": {
        "prompt": """list some keywords of the following:
        {doc}
        CONCISE KEYWORDS:""",
        "refine_prompt": (
            "Your job is to produce some final keywords\n"
            "We have provided some keywords up to a certain point: {existing_answer}\n"
            "We have the opportunity to refine the existing keywords"
            "(only if needed) with some more context below.\n"
            "------------\n"
            "{text}\n"
            "------------\n"
            "Given the new context, refine the original keywords in {lang}"
            "If the context isn't useful, return the original keywords in {lang}."
            "Output the keywords directly, do not add any prefixes"
        )
    },
    "comments": {
        "prompt": """Write some comments of the following:
        {doc}
        CONCISE COMMENTS:""",
        "refine_prompt": (
            "Your job is to produce some final comments\n"
            "We have provided some comments up to a certain point: {existing_answer}\n"
            "We have the opportunity to refine the existing comments"
            "(only if needed) with some more context below.\n"
            "------------\n"
            "{text}\n"
            "------------\n"
            "Given the new context, refine the original comments in {lang}"
            "If the context isn't useful, return the original comments in {lang}."
            "do not add any prefixes, do not indicate the line numbers or paragraphs in output,Given the comments directly."
        )
    }
}

shortcut_keys = shortcut_data.keys()

shortcut_instance = dict(Shortcut(**shortcut_data))