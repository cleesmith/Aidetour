# requirements.txt:
# pip install -U fastapi
# pip install -U httpx
# pip install -U pydantic
# pip install -U uvicorn

'''
curl -i -X POST -H "Content-Type: application/json" -d '{                     
  "model": "gpt-3.5-turbo",
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
  "stream": false
}' http://localhost:8000/v1/chat/completions
'''

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
import httpx
import json
import os
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

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

@app.get("/v1/models")
def list_models():
    models = {
        "object": "list",
        "data": [
            {
                "id": "gpt-3.5-turbo",
                "object": "model",
                "created": 1677610602,
                "owned_by": "openai"
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
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }
        response = await client.post(OPENAI_API_URL, content=await request.body(), headers=headers, timeout=None)

    async def generate():
        async for chunk in response.aiter_bytes():
            print(f"{chunk}")
            yield chunk

    return StreamingResponse(generate(), status_code=response.status_code, media_type="application/json")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=1)

