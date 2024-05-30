# requirements.txt:
# fastapi
# httpx
# pydantic
# uvicorn

# curl -i -X POST -H "Content-Type: application/json" -d '{"message":"what is the capital of the united states?"}' http://localhost:8000

# import traceback
# import json
# import os
# from typing import AsyncGenerator
# import httpx
# from fastapi import FastAPI
# from fastapi.responses import StreamingResponse
# from pydantic import BaseModel

# import uvicorn

# API_KEY = os.environ["OPENAI_API_KEY"]
# TIMEOUT = 30

# app = FastAPI()

# class ResponseMessage(BaseModel):
#     content: str

# class RequestMessage(BaseModel):
#     message: str

# async def openai_stream(data: dict) -> AsyncGenerator[str, None]:
#     async with httpx.AsyncClient() as client:
#         async with client.stream(
#             "POST",
#             "https://api.openai.com/v1/chat/completions",
#             timeout=httpx.Timeout(TIMEOUT),
#             headers={
#                 "Authorization": f"Bearer {API_KEY}",
#             },
#             json=data,
#         ) as response:
#             print(f"received response status_code={response.status_code}")
#             response.raise_for_status()
#             async for chunk in response.aiter_text():
#                 yield chunk

# async def response_generator(message: str) -> AsyncGenerator[str, None]:
#     async for response in openai_stream(
#         {
#             "messages": [
#                 {"role": "system", "content": "You are a helpful assistant"},
#                 {"role": "user", "content": message},
#             ],
#             "model": "gpt-3.5-turbo-16k-0613",
#             "stream": True,
#         }
#     ):
#         buffer = ""
#         buffer += response  # Accumulate response chunks
#         try:
#             while "\n" in buffer:  # Check if there are complete JSON objects
#                 line, buffer = buffer.split("\n", 1)
#                 if line.strip():  # Ensure the line has content before processing

#                     try:
#                         data = json.loads(line)
#                         yield ResponseMessage(content=data['text']).json() + "\n"
#                     except json.JSONDecodeError as e:
#                         tb_info = traceback.format_exc()
#                         print(f"Failed to decode JSON: {str(e)}\nTraceback details:\n{tb_info}")
#                         continue
#         except json.JSONDecodeError as e:
#             tb_info = traceback.format_exc()
#             print(f"Failed to decode JSON: {str(e)}\nTraceback details:\n{tb_info}")

# @app.post("/")
# async def message(request: RequestMessage):
#     print(f"\n request:\n{request}\nrequest.message={request.message}\n")
#     return StreamingResponse(
#         response_generator(request.message),
#         media_type="text/event-stream"
#     )

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)


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
    print("Received request:")
    print(f"Method: {request.method}")
    print(f"URL: {request.url}")
    print(f"Headers: {request.headers}")
    print(f"Body: {await request.body()}")
    print("-----------------")
    # forward the incoming request to the OpenAI API
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
