import requests

import logging
logging.basicConfig(
    format="%(levelname)s [%(asctime)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG
)
logging.basicConfig(level=logging.DEBUG)

s = requests.Session()
s.mount('http://', requests.adapters.HTTPAdapter(max_retries=0))
try:
    response = s.get("http://127.0.0.1:5600/")
except Exception as e:
    print(f"cls_req:\nAn unexpected error occurred:\n\"{e}\"\ntheEnd.")
finally:
    response = None
    s.close()
    print(f"cls_req:\nfinally: s.close().")



# import requests
# try:
#     response = requests.get("http://127.0.0.1:5600/")
#     print(f"ping_server: response={response}")
# except Exception as e:
#     print(f"Caught Exception: {type(e)} - {e}")


# import httpx
# import json
# import logging

# logging.basicConfig(
#     format="%(levelname)s [%(asctime)s] %(name)s - %(message)s",
#     datefmt="%Y-%m-%d %H:%M:%S",
#     level=logging.DEBUG
# )

# # Configure logging to ignore unwanted logs from httpx
# logging.basicConfig(level=logging.DEBUG)
# logging.getLogger("httpx").setLevel(logging.CRITICAL)

# headers = {
#     "anthropic-version": "2023-06-01",
#     "anthropic-beta": "messages-2023-12-15",
#     "content-type": "application/json",
#     "x-api-key": "what???"
# }
# data = {
#     "model": "claude-3-haiku-20240307",
#     "messages": [{"role": "user", "content": "Hello"}],
#     "max_tokens": 4096,
#     "stream": True
# }
# url = "http://127.0.0.1:5600/" #"https://api.anthropic.com/v1/messages"
# timeout = 2
# try:
#     transport = httpx.HTTPTransport(retries=0)
#     # transport = httpx.WSGITransport(app=app) # see: https://www.python-httpx.org/advanced/transports/#http-transport
#     print("cls_req: Attempting to POST data...")
#     with httpx.Client(transport=transport, timeout=timeout) as client:
#         # response = client.post(url, headers=headers, json=data)
#         response = client.get(url, headers=headers)
#         response.raise_for_status()  # Will raise an exception for 4XX/5XX responses
#         print("cls_req: Response received successfully:")
#         # json_data = response.get_json()
#         print(f"\ncls_req: response={response}\n")
#         line_count = 0
#         for line in response.iter_lines():
#             print(f"\nline={line}")
#             line_count += 1
#             # maybe no special handling of "event: message_stop" since that's the last line in response ?
#             if line:
#                 if "data: " in line:
#                     event_data_json = line.split("data: ", 1)[1]
#                     event_data = json.loads(event_data_json)  # convert the JSON part to a Python dict
#                     print(f"\nevent_data={event_data}")

#         print(f"\nlines={line_count}")

# except httpx.TimeoutException as e:
#     print(f"cls_req: Request timed out after {timeout} seconds")
# except httpx.RequestError as e:
#     print(f"cls_req: Request error occurred: {e}")
# except httpx.HTTPStatusError as e:
#     print(f"cls_req: HTTP error occurred: {e.response.status_code} - {e.response.text}")
# except Exception as e:
#     print(f"cls_req: An unexpected error occurred: {e}")
