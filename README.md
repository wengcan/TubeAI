# TubeAI
Use LangChain and Google Gemini Pro to Summarize Youtube Video Contents

## Current Features
- Generate Summarization,Keywords,Comments  For YouTube Video 
- Output language support

Example Usage
```
    curl --location 'http://127.0.0.1:8080/shortcut/summarize' \
    --header 'Content-Type: application/json' \
    --data '{
        "url":"https://www.youtube.com/watch?v=H2qLoaetLJM",
        "lang": "zh"
    }'
```

## Upcoming Features
- Web Interface
- YouTube Video Questioning
- Docker Image Integration