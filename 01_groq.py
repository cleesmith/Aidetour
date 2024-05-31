# requirements.txt:
# pip install -U fastapi
# pip install -U httpx
# pip install -U pydantic
# pip install -U uvicorn

'''
test directly to Groq:
curl -X POST "https://api.groq.com/openai/v1/chat/completions" \
     -H "Authorization: Bearer $GROQ_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"messages": [{"role": "user", "content": "hi!"}], "model": "llama3-8b-8192"}'
'''

'''
get a list of models from Groq:
curl -X GET "https://api.groq.com/openai/v1/models" \
     -H "Authorization: Bearer $GROQ_API_KEY" \
     -H "Content-Type: application/json"

{"object":"list","data":[{"id":"gemma-7b-it","object":"model","created":1693721698,"owned_by":"Google","active":true,"context_window":8192},{"id":"llama3-70b-8192","object":"model","created":1693721698,"owned_by":"Meta","active":true,"context_window":8192},{"id":"llama3-8b-8192","object":"model","created":1693721698,"owned_by":"Meta","active":true,"context_window":8192},{"id":"mixtral-8x7b-32768","object":"model","created":1693721698,"owned_by":"Mistral AI","active":true,"context_window":32768}]}
'''

'''
curl -i -X POST -H "Content-Type: application/json" -d '{                     
  "model": "llama3-70b-8192",
  "messages": [        
    {                                          
      "role": "system",
      "content": "You are a helpful assistant."
    },               
    {                                 
      "role": "user",
      "content": "Hello, how are you?"
    }           
  ],
  "stream": true
}' http://localhost:8000/v1/chat/completions
'''

import os
import time
import datetime
import json
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
import httpx
import uvicorn

app = FastAPI()

# configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GROQ_API_KEY = os.environ["GROQ_API_KEY"]
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


# curl -X GET "http://localhost:8000/v1/models"
@app.get("/v1/models")
def list_models():
    '''
    see: https://console.groq.com/docs/models
    Model ID: llama3-8b-8192
    Developer: Meta
    Context Window: 8,192 tokens
    Knowledge cutoff: December, 2023
    cls: when you need to make up a "created" timestamp:
    date = datetime.datetime(2023, 12, 31)
    # convert the datetime object to a Unix timestamp
    timestamp = int(time.mktime(date.timetuple()))
    '''
    models = {
        "object": "list",
        "data": [
            {
                "id": "llama3-70b-8192",
                "object": "model",
                "created": 1693721698,
                "owned_by": "Meta"
            }
        ]
    }
    return JSONResponse(content=models)

@app.post("/v1/chat/completions")
async def chat_completion(request: Request):
    print("\nRequest:")
    print(f"Method: {request.method}")
    print(f"URL: {request.url}")
    print(f"Headers: {request.headers}")
    print(f"Body: {await request.body()}")
    print("-----------------")
    # forward the incoming request to the backend API
    async with httpx.AsyncClient() as client:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GROQ_API_KEY}"
        }
        response = await client.post(GROQ_API_URL, content=await request.body(), headers=headers, timeout=None)

    async def generate():
        async for chunk in response.aiter_bytes():
            print(f"{chunk}")
            yield chunk

    return StreamingResponse(generate(), status_code=response.status_code, media_type="application/json")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=1)

