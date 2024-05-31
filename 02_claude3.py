# requirements.txt:
# pip install -U fastapi
# pip install -U httpx
# pip install -U pydantic
# pip install -U uvicorn

'''
test directly to Anthropic:
curl https://api.anthropic.com/v1/messages \
     --header "x-api-key: $ANTHROPIC_API_KEY" \
     --header "anthropic-version: 2023-06-01" \
     --header "content-type: application/json" \
     --data '{
         "model": "claude-3-haiku-20240307",
         "max_tokens": 1024,
         "messages": [
             {"role": "user", "content": "Hi!"}
         ]
     }'
'''

'''
curl -i -X POST -H "Content-Type: application/json" -d '{                     
  "model": "claude-3-haiku-20240307",
  "max_tokens": 4000,
  "messages": [        
    {                                 
      "role": "user",
      "content": "Hi!"
    }           
  ],
  "stream": true
}' http://localhost:8000/v1/chat/completions
'''

import os
import time
import datetime
import json
import uuid
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
import httpx
import uvicorn

CLAUDE_MODEL = "claude-3-haiku-20240307" # default = inexpensive

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"


def generate_unique_string():
    unique_id = str(uuid.uuid4())
    unique_id = unique_id.replace("-", "")
    unique_id = unique_id[:24]
    unique_string = "msg_" + unique_id
    print(f"generate_unique_string: {unique_string}")
    return unique_string

def set_claude_model(original_body):
    global CLAUDE_MODEL
    body_dict = json.loads(original_body)

def convert_body_for_anthropic(original_body):
    '''
    cls: something like this expected by anthropic:
    '{
        "model": "claude-3-haiku-20240307",
        "max_tokens": some_number_if_sent,
        "system": "some_system_message_if_sent", 
        "messages": [{"role": "user", "content": "Hello"}],
    }'
    novelcrafter errors via anthropic api:
    Error running prompt: Error: 400 max_tokens: Field required
    Error running prompt: Error: 400 frequency_penalty: Extra inputs are not permitted
    '''
    set_claude_model(original_body)

    body_dict = json.loads(original_body)
    
    # extract the system message if it exists
    system_message = next(
        (msg['content'] for msg in body_dict['messages'] if msg['role'] == 'system'), 
        None
    )
    
    # remove the system message from messages list if it exists
    body_dict['messages'] = [
        msg for msg in body_dict['messages'] if msg['role'] != 'system'
    ]
    
    CLAUDE_MODEL = body_dict.get("model")
    # construct the new body for Anthropic
    anthropic_body = {
        "model": CLAUDE_MODEL,
        "messages": body_dict.get("messages"),
        "max_tokens": body_dict.get("max_tokens", 4000)  # Default to 4000 if not provided
    }
    
    # add the system message if it exists
    if system_message:
        anthropic_body["system"] = system_message
    
    # include only the allowed parameters
    allowed_keys = [
        "stream", "temperature", 
        "top_k", "top_p", "id",
        "stop_sequences"
    ]
    for key in allowed_keys:
        if key in body_dict:
            anthropic_body[key] = body_dict[key]
    
    print(f"\n anthropic_body={anthropic_body} \n")
    return json.dumps(anthropic_body)


# curl -X GET "http://localhost:8000/v1/models"
@app.get("/v1/models")
def list_models():
    '''
    a list of models from Anthropic:
        claude-3-opus-20240229
        claude-3-sonnet-20240229
        claude-3-haiku-20240307
    Max output for all Claude3 models: 4096 tokens
    see: https://docs.anthropic.com/en/docs/models-overview#model-comparison
    see: https://console.groq.com/docs/models
    Developer: Anthropic
    Context Window: 200K tokens
    Knowledge cutoff: August 2023
    cls: when you need to make up a "created" timestamp:
    date = datetime.datetime(2023, 12, 31)
    # convert the datetime object to a Unix timestamp
    timestamp = int(time.mktime(date.timetuple()))
    '''
    models = {
        "object": "list",
        "data": [
            {
                "id": "claude-3-haiku-20240307",
                "object": "model",
                "created": 1693454400,
                "owned_by": "Anthropic"
            }
        ]
    }
    return JSONResponse(content=models)

@app.post("/v1/chat/completions")
async def chat_completion(request: Request):
    print("\nRequest:")
    print(f"Method: {request.method}")
    print(f"URL: {request.url}")
    # headers = dict(request.headers)
    # print(f"Headers: {json.dumps(headers, indent=4)}")
    body = await request.body()
    print(f"Body: {body.decode('utf-8')}")
    print("-----------------")
    
    set_claude_model(body)

    body_dict = json.loads(body)
    stream = body_dict.get("stream", False)

    # convert the body to the format expected by Anthropic
    converted_body = convert_body_for_anthropic(body)
    print(f"Converted Body: {converted_body}")
    
    # forward the incoming request to the Anthropic API
    async with httpx.AsyncClient() as client:
        headers = {
            "anthropic-version": "2023-06-01",
            # "anthropic-beta": "messages-2023-12-15",
            "content-type": "application/json",
            "x-api-key": f"{ANTHROPIC_API_KEY}"
        }
        response = await client.post(ANTHROPIC_API_URL, content=converted_body, headers=headers, timeout=None)
    
    '''
        async def generate():
            message_id = generate_unique_string()
            if stream:
                async for line in response.aiter_lines():
                    print(f"Line: {line}")
                    if line:
                        # In the context of using httpx's aiter_lines(), the lines are already strings, 
                        # so decoded_line = line is sufficient and avoids the extra decoding step:
                        # decoded_line = line.decode('utf-8')
                        decoded_line = line

                        if "error" in decoded_line:
                            continue  # the next response line received should be "data: ...overloaded_error..."

                        if "message_start" in decoded_line:
                            continue

                        # check if "data: " is in the decoded line and split accordingly
                        if "data: " in decoded_line:
                            try:
                                event_data_json = decoded_line.split("data: ", 1)[1]
                                event_data = json.loads(event_data_json)  # convert the JSON part to a Python dict

                                if event_data.get("type") == "error":
                                    transformed_error_data = {
                                        "id": message_id,
                                        "object": "chat.completion.chunk",  # would "error" work ?
                                        "created": int(time.time()),
                                        "model": CLAUDE_MODEL,
                                        "choices": [{
                                            "index": 0,
                                            "delta": {
                                                "role": "system",
                                                "content": f'{response.status_code}: {event_data["error"]["message"]}',
                                            },
                                            "finish_reason": "error"
                                        }]
                                    }

                                    yield f"data: {json.dumps(transformed_error_data)}\n\n"
                                    yield "data: [DONE]\n\n"
                                    continue

                                if event_data.get('type') == 'message_stop':
                                    transformed_data = {
                                        "id": message_id,
                                        "object": "chat.completion.chunk",
                                        "created": int(time.time()),
                                        "model": CLAUDE_MODEL,
                                        "choices": [{
                                            "index": 0,
                                            "delta": {},
                                            "finish_reason": "stop"
                                        }]
                                    }

                                    yield f"data: {json.dumps(transformed_data)}\n\n"
                                    yield "data: [DONE]\n\n"
                                    continue

                                if event_data.get('type') == 'content_block_delta':
                                    transformed_data = {
                                        "id": message_id,
                                        "object": "chat.completion.chunk",
                                        "created": int(time.time()),
                                        "model": CLAUDE_MODEL,
                                        "choices": [{
                                            "index": 0,
                                            "delta": {
                                                "role": "assistant",
                                                "content": event_data['delta']['text'],
                                            },
                                            "finish_reason": None
                                        }]
                                    }
                                    yield f"data: {json.dumps(transformed_data)}\n\n"

                            except json.JSONDecodeError:
                                print(f"Could not decode JSON from: {decoded_line}")
                            except IndexError:
                                print(f"Unexpected format for: {decoded_line}")
                    else:
                        # not "data: " ... maybe a line like: "event: content_block_start"
                        if "event: " in decoded_line:
                            event_data_json = decoded_line.split("event: ", 1)[1]
                            if event_data_json in ('message_start', 'content_block_start', 'content_block_delta', 'ping', 'content_block_stop', 'message_delta', 'message_stop', 'error'):
                                continue
                else:
                    response_data = await response.json()
                    transformed_data = {
                        "id": message_id,
                        "object": "chat.completion",
                        "created": int(time.time()),
                        "model": CLAUDE_MODEL,
                        "choices": [{
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": "".join([content["text"] for content in response_data["content"]]),
                            },
                            "finish_reason": response_data["stop_reason"]
                        }]
                    }
        
        return StreamingResponse(generate(), media_type="text/event-stream")
    '''

    if stream:
        async def generate():
            message_id = generate_unique_string()
            async for line in response.aiter_lines():
                print(f"Line: {line}")
                if line:
                    decoded_line = line

                    if "error" in decoded_line:
                        continue

                    if "message_start" in decoded_line:
                        continue

                    if "data: " in decoded_line:
                        try:
                            event_data_json = decoded_line.split("data: ", 1)[1]
                            event_data = json.loads(event_data_json)

                            if event_data.get("type") == "error":
                                transformed_error_data = {
                                    "id": message_id,
                                    "object": "chat.completion.chunk",
                                    "created": int(time.time()),
                                    "model": CLAUDE_MODEL,
                                    "choices": [{
                                        "index": 0,
                                        "delta": {
                                            "role": "system",
                                            "content": f'{response.status_code}: {event_data["error"]["message"]}',
                                        },
                                        "finish_reason": "error"
                                    }]
                                }
                                yield f"data: {json.dumps(transformed_error_data)}\n\n"
                                yield "data: [DONE]\n\n"
                                continue

                            if event_data.get('type') == 'message_stop':
                                transformed_data = {
                                    "id": message_id,
                                    "object": "chat.completion.chunk",
                                    "created": int(time.time()),
                                    "model": CLAUDE_MODEL,
                                    "choices": [{
                                        "index": 0,
                                        "delta": {},
                                        "finish_reason": "stop"
                                    }]
                                }
                                yield f"data: {json.dumps(transformed_data)}\n\n"
                                yield "data: [DONE]\n\n"
                                continue

                            if event_data.get('type') == 'content_block_delta':
                                transformed_data = {
                                    "id": message_id,
                                    "object": "chat.completion.chunk",
                                    "created": int(time.time()),
                                    "model": CLAUDE_MODEL,
                                    "choices": [{
                                        "index": 0,
                                        "delta": {
                                            "role": "assistant",
                                            "content": event_data['delta']['text'],
                                        },
                                        "finish_reason": None
                                    }]
                                }
                                yield f"data: {json.dumps(transformed_data)}\n\n"

                        except json.JSONDecodeError:
                            print(f"Could not decode JSON from: {decoded_line}")
                        except IndexError:
                            print(f"Unexpected format for: {decoded_line}")
                    else:
                        if "event: " in decoded_line:
                            event_data_json = decoded_line.split("event: ", 1)[1]
                            if event_data_json in ('message_start', 'content_block_start', 'content_block_delta', 'ping', 'content_block_stop', 'message_delta', 'message_stop', 'error'):
                                continue

        return StreamingResponse(generate(), media_type="text/event-stream")
    else:
        message_id = generate_unique_string()
        response_data = response.json()
        transformed_data = {
            "id": message_id,
            "object": "chat.completion",
            "created": int(time.time()),
            "model": CLAUDE_MODEL,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "".join([content["text"] for content in response_data["content"]]),
                },
                "finish_reason": response_data["stop_reason"]
            }]
        }
        return JSONResponse(content=transformed_data)



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=1)

