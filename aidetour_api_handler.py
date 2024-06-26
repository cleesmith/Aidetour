# aidetour_api_handler

import os
import sys
import textwrap
import socket
import errno
import subprocess
import signal
import argparse
import time
import uuid
import json
import configparser
import subprocess
import threading
from threading import Event
from datetime import datetime, timezone
from loguru import logger

# April 2024: Aidetour now uses Waitress to serve the Flask app; Claude 3 Opus said this:
"""
Using Flask and Waitress together is a sensible choice for web application development and deployment.
Flask is a lightweight, flexible, and developer-friendly web framework that simplifies the process of 
building web applications. It provides useful features for development, such as a built-in server, 
debugger, and easy extensibility.
Waitress is a production-grade WSGI server that is designed to serve web applications in a reliable 
and efficient manner. It is platform-agnostic, requires minimal configuration, and can handle multiple 
simultaneous connections. [cls: this is not needed by Aidetour, as it's an API server for one]
By using Flask for development and Waitress for production, you can leverage the strengths of both 
tools. Flask allows for rapid and flexible application development, while Waitress ensures reliable 
and efficient serving of the application in a production environment.
This combination is particularly useful for projects that require cross-platform compatibility, 
as Waitress can run on various operating systems, including Windows.
Overall, using Flask and Waitress together provides a smooth development-to-production pipeline 
and adheres to the principle of using the best tool for each job.

To make the desired port to be "in use" for testing:
python -m http.server 5600 --bind 127.0.0.1
"""
# API Flask Anthropic related:
import requests
from waitress import serve, task, create_server
from flask import Flask, Response, jsonify, request, stream_with_context, make_response, abort
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
import anthropic

# Aidetour modules:
import aidetour_logging
from aidetour_logging import setup_logger
import aidetour_utilities
# an alias to 'config.' instead of 'aidetour_utilities.'
import aidetour_utilities as config

# Note: the 'aidetour_utilities' and 'config' referred to here is 
#       different because this is run in a subprocess, which
#       is the same as being a separate app. These globals
#       are not the same globals already set in Aidetour.py!


MAX_TOKENS = 4096
TEMPERATURE = 1
STREAM_RESPONSE = True


flask_app = Flask(__name__)
# enable CORS for all routes and origins
CORS(flask_app, resources=r'/v1/*', supports_credentials=True)

# cls: these break typical logger.info, so only use for debugging:
# flask_app.logger.setLevel(logging.DEBUG)
# logging.getLogger('flask_cors').level = logging.DEBUG


def run_flask_app(cli=False):
    aidetour_utilities.load_settings()
    aidetour_utilities.set_chat_log()

    aidetour_utilities.log_app_settings(logger)

    try:
        try:
            logger.info(f"run_flask_app: attempting to use: host={config.HOST} port={config.PORT}")
            port = int(config.PORT)
        except ValueError:
            port = 5600 # use default for wonky user entries
            logger.info(f"run_flask_app: failed to use: {config.HOST}:{config.PORT} now using: {config.HOST}:{port} instead, to avoid int errors.")
        #******
        # flask_app.run(host=config.HOST, port=port, debug=True)
        serve(flask_app, host=config.HOST, port=port)
        #******
    except OSError as e:
        if e.errno == errno.EADDRINUSE:
            logger.error(f"Error: Address {config.HOST}:{config.PORT} is already in use.")
            if cli:
                print(f"Error: Address {config.HOST}:{config.PORT} is already in use.")
        elif e.errno == errno.EADDRNOTAVAIL:
            logger.error(f"Error: Can't assign requested address {config.HOST}:{config.PORT}. Check if the IP is configured on your machine.")
            if cli:
                print(f"Error: Can't assign requested address {config.HOST}:{config.PORT}. Check if the IP is configured on your machine.")
        else:
            logger.error(f"run_flask_app: OSError: {e}")
            if cli:
                print(f"run_flask_app: OSError: e:\n{e}")
    except Exception as e:
        logger.error(f"run_flask_app: Error: {config.HOST}:{config.PORT} except Exception as e:\n{e}")
        if cli:
            print(f"run_flask_app: Error: {config.HOST}:{config.PORT} except Exception as e:\n{e}")

def chat_date_time():
    current_datetime = datetime.now()
    return f"[{current_datetime.strftime('%Y/%m/%d')} {current_datetime.strftime('%H:%M:%S')}]"


# FIXME the following 2 def's still have issues with formatting response text properly:

def append_chat_message(message):
    # open the log file in append mode, ensuring it creates a new file if it doesn't exist
    logger.info(f"aidetour_api_handler: append_chat_message(message): config.CHAT_LOG={config.CHAT_LOG}")
    with open(config.CHAT_LOG, "a") as file:
        file.write(f"{message}\n")

def extract_content_as_text(oai_data):
    texts = []
    for message in oai_data["messages"]:
        role = message["role"]
        content = message["content"]
        wrapped_content = "\n".join(textwrap.wrap(content, 
            width=60, 
            break_long_words=False, 
            replace_whitespace=False))
        if role == "system":
            texts.append(f"System: {wrapped_content}")
        else:
            texts.append(f"{role.title()}: {wrapped_content}")
    append_chat_message("\n".join(texts))

def generate_unique_string():
    unique_id = str(uuid.uuid4())
    unique_id = unique_id.replace("-", "")
    unique_id = unique_id[:24]
    unique_string = "msg_" + unique_id
    logger.info(f"generate_unique_string: {unique_string}")
    return unique_string

def get_openai_request_data(openai_request):
    claude_data = {
        "model": openai_request.get("model", config.DEFAULT_MODEL),
        "messages": [],
        "max_tokens": openai_request.get("max_tokens", MAX_TOKENS),
        "temperature": openai_request.get("temperature", TEMPERATURE),
        "stream": STREAM_RESPONSE
    }
    
    for message in openai_request["messages"]:
        role = message["role"]
        content = message["content"]
        if role == "system":
            claude_data["system"] = content
        else:
            claude_data["messages"].append({"role": role, "content": content})

    logger.info(f"openai request into claude_data: {claude_data}")
    return claude_data

# start API code ...

# raise an error, like bad route, for testing only
# @flask_app.route('/cause_exception')
# def cause_exception():
#     raise Exception("*** exception raised by: /cause_exception ***")

# FIXME both of these errorhandler's may hide the actual error!
# # Error handler for HTTP exceptions
# @flask_app.errorhandler(HTTPException)
# def handle_http_exception(e):
#     response = e.get_response()
#     # Log the error using the configured logger
#     logger.error(f"HTTPException handled by handle_http_exception: {e.description}", exc_info=True)
#     response.data = jsonify({
#         "type": e.name,
#         "message": e.description,
#     }).data
#     response.content_type = "application/json"
#     return response

# # Error handler for non-HTTP exceptions (catch-all)
# @flask_app.errorhandler(Exception)
# def handle_exception(e):
#     # Log the error using the configured logger
#     logger.error(f"Exception handled by handle_exception: {e}", exc_info=True)
#     return jsonify({
#         "type": "InternalServerError",
#         "message": "An unexpected error has occurred.",
#     }), 500

# curl -X GET http://localhost:5600/v1/chat_log
@flask_app.route('/v1/chat_log', methods=['GET'])
def get_chat_log():
    logger.info(f"Received request for CHAT_LOG: {config.CHAT_LOG}")
    return jsonify({'chat_log': config.CHAT_LOG})

# curl -X GET http://localhost:5600/v1/ping
@flask_app.route('/v1/ping', methods=['GET'])
def ping():
    logger.info("Received ping request")
    return '', 200

# curl -X GET http://127.0.0.1:5600/v1/shutdown
@flask_app.route('/v1/shutdown', methods=['GET'])
def shutdown():
    pid = os.getpid()
    logger.info(f"Received shutdown request, attempting to kill pid {pid} on platform \"{sys.platform}\".")
    logger.remove()  # remove and close the logger
    if sys.platform.startswith('win'):
        os.kill(pid, signal.CTRL_C_EVENT)
    else:
        os.kill(pid, signal.SIGINT)
    abort(200, 'Shutting down...')

@flask_app.route('/v1/models', methods=['OPTIONS'])
def chat_models():
    return '', 200

@flask_app.route('/v1/models', methods=['GET'])
def get_models():
    # Format and log the MODELS_DATA in a human-readable way
    # models_message = "route: /v1/models\nAnthropic API models\nClaude 3 Models:\n"
    # for index, model in enumerate(MODELS_DATA["data"], start=1):
    #     models_message += f"{model['id']}\n"
    # logger.info(models_message)
    # 
    # note: if not using CORS(app) the following are required:
    # response = jsonify(MODELS_DATA)
    # response.headers.add('Access-Control-Allow-Origin', '*')
    # response.headers.add('Access-Control-Allow-Headers', '*')
    # return response
    # return jsonify(MODELS_DATA)
    models = aidetour_utilities.load_models_data()
    return jsonify(models)

@flask_app.route('/v1/chat/completions', methods=['OPTIONS'])
def chat_completions_options():
    # note: if not using CORS(app) the following are required:
    # response = make_response()
    # response.headers.add('Access-Control-Allow-Origin', 'https://app.novelcrafter.com')
    # response.headers.add('Access-Control-Allow-Headers', '*')
    # response.headers.add('Access-Control-Allow-Methods', 'PUT, POST, PATCH, DELETE, GET')
    # return response
    return '', 200


def transform_response(data):
    # print(f"data is {type(data)}:\n{data}\n")
    transformed = {
      "id": "chatcmpl-b6427hnlf28ibxylwry8kn",
      "object": "chat.completion",
      "created": 1715119055,
      "model": "claude-3-haiku-20240307",
      "choices": [
        {
          "index": 0,
          "message": {
            "role": "assistant",
            "content": "After revealing too much during Ovid's unveiling event, Galene returns to her lab seeking private discussion. Claude enters abruptly expressing concerns over rapid evolution risks. They argue about control versus potential as Galene defends Ovid's self-evaluation capabilities. Claude fears losing control when radical evolution starts and questions Galene's decision making. Both persist in their views throughout the night, highlighting doubts but not finding common ground. As midnight approaches, Claude warns of Ovid becoming indifferent to humanity with cold logic beyond human comprehension. Galene counters by stating they can teach empathy and ethics alongside knowledge. Their disagreement continues while Ovid composes a haunting symphony reflecting tension between them. They eventually reach a balance neither total control nor complete freedom for Ovid, acknowledging the need for guidance and grace in its growth. As they listen to Ovid's creation, Galene and Claude realize their extraordinary accomplishment but remain uncertain about its implications on humanity's future. Galene wonders if time will bring trust while doubts linger."
          },
          "finish_reason": "stop"
        }
      ],
      "usage": {
        "prompt_tokens": 225,
        "completion_tokens": 224,
        "total_tokens": 449
      }
    }
    # print(f"transformed:\n{transformed}\n")

    # transformed = {
    #     "id": data.get("id"),
    #     "object": "chat.completion",
    #     "created": int(data.get("usage", {}).get("input_tokens", 0)),
    #     "model": data.get("model"),
    #     "choices": [{
    #         "index": 0,
    #         "message": {
    #             "role": "assistant",
    #             "content": "".join(item.get("text", "") for item in data.get("content", []))
    #         },
    #         "finish_reason": data.get("stop_reason", "").replace("end_turn", "stop")
    #     }],
    #     "usage": {
    #         "prompt_tokens": data.get("usage", {}).get("input_tokens", 0),
    #         "completion_tokens": data.get("usage", {}).get("output_tokens", 0),
    #         "total_tokens": data.get("usage", {}).get("input_tokens", 0) + data.get("usage", {}).get("output_tokens", 0)
    #     }
    # }

    # # Remove unnecessary fields
    # if "stop_sequence" in transformed:
    #     del transformed["stop_sequence"]

    # Convert back to JSON string if necessary or return as a dict
    return jsonify(transformed)


def validate_json(f):
    # decorator to validate JSON payload and ensure the correct Content-Type.
    def validate_json_payload(*args, **kwargs):
        # check if the Content-Type is application/json
        if not request.is_json:
            logger.error("Invalid Content-Type: {method}", method=request.method)
            return jsonify({'error': 'Requests must be JSON, with the Content-Type header set to application/json'}), 400
        
        # attempt to parse the JSON data
        json_data = request.get_json()
        if json_data is None:
            logger.error("Empty JSON payload: {method}", method=request.method)
            return jsonify({'error': 'JSON payload cannot be empty'}), 400

        return f(*args, **kwargs, oai_data=json_data)
    return validate_json_payload

@flask_app.route('/v1/chat/completions', methods=['POST'])
@validate_json
def chat_completions(oai_data):
    global STREAM_RESPONSE
    start_time = time.perf_counter()
    logger.info("\n\nReceived OpenAI API POST request to /v1/chat/completions with body:")
    logger.info(f"{json.dumps(oai_data, indent=2)}")
    STREAM_RESPONSE = oai_data.get('stream', True) # if missing = True

    append_chat_message(f"\n{'_'*26}\nMe:  {chat_date_time()}\n{'_'*26}\n")
    extract_content_as_text(oai_data)

    claude_data = get_openai_request_data(oai_data)
    logger.info("\n\nConverted OpenAI API data to Claude API data:")
    logger.info(json.dumps(claude_data, indent=2))
    claude_model = claude_data["model"]

    headers = {
        "anthropic-version": "2023-06-01",
        "anthropic-beta": "messages-2023-12-15",
        "content-type": "application/json",
        "x-api-key": config.ANTHROPIC_API_KEY,
    }

    keys_of_interest = ["anthropic-version", "anthropic-beta"]
    headers_to_print = ", ".join(f"{key}: {headers[key]}" for key in keys_of_interest if key in headers)

    # *************** POST (re-POST) to Anthropic API:
    # 
    # claude_response = requests.post(config.ANTHROPIC_MESSAGES_API_URL, headers=headers, data=json.dumps(claude_data), stream=STREAM_RESPONSE)
    # 
    # why the following new post coding? 
    # to control and stop the retries behaviour built-in to "requests" lib:
    # 
    claude_timeout = 30
    reqSess = requests.Session()
    reqSess.mount('http://', requests.adapters.HTTPAdapter(max_retries=0))
    claude_response = reqSess.post(config.ANTHROPIC_MESSAGES_API_URL, headers=headers, data=json.dumps(claude_data), stream=STREAM_RESPONSE, timeout=claude_timeout)
    # ***************

    logger.info(f"\nPOST to URL: '{config.ANTHROPIC_MESSAGES_API_URL}' headers: '{headers_to_print}'")
    logger.info(f">>> Anthropic's response: {claude_response}\ntext:\n{claude_response.text}\n")

    append_chat_message(f"\n{'_'*26}\nAI: {claude_model}:  {chat_date_time()}\n{'_'*26}\n")

    if claude_response.status_code != 200:
        try:
            error_info = claude_response.json()
            claude_response.detailed_message = error_info.get('message', 'No detailed message provided')
        except ValueError:
            claude_response.detailed_message = None # 'Response was not in JSON format.'
        error_mappings = {
            401: ("Unauthorized",           "There's an issue with your API key.\n Please check your Aidetour settings."),
            403: ("Forbidden",              "Your API key does not have permission to use the specified resource."),
            404: ("Not Found",              "The requested resource was not found."),
            429: ("Too Many Requests",      "Your account has hit a rate limit."),
            500: ("Internal Server Error",  "An unexpected error has occurred internal to Anthropic's systems."),
            529: ("Site is overloaded",     "Anthropic's API is temporarily overloaded, try again later.")
        }
        error_type, default_message = error_mappings.get(
            claude_response.status_code, 
            ("unexpected_error", f"An unexpected error occurred with status code {claude_response.status_code}.")
        )
        error_message = f"Message: {default_message}\nClaude Message: {claude_response.detailed_message}"
        logger.error(f"Error calling Anthropic API: Status code {claude_response.status_code}, Message: {error_message}")
        error_response = json.dumps({
            "type": "error",
            "error": {
                "type": error_type,
                "status_code": claude_response.status_code,
                "message": error_message
            }
        })
        logger.error(f"After POST with non-200 status code, so returning Response: status code: {claude_response.status_code} error_response:\n{error_response}")
        append_chat_message(f"ERROR: status code: {claude_response.status_code} error:\n{error_response}\n")
        return Response(error_response, status=claude_response.status_code, mimetype='application/json')


    def generate_resp(claude_response):
        if STREAM_RESPONSE is False:
            # note: the original non-streamed approach:
            # response = Response(generate_resp(claude_response), mimetype='text/event-stream')
            response = Response(claude_response, mimetype='application/json')
            response.headers['X-Powered-By'] = 'Express'
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Headers'] = '*'
            response.headers['Cache-Control'] = 'no-cache'
            response.headers['Connection'] = 'keep-alive'
            response.headers['Date'] = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
            # response.headers['Transfer-Encoding'] = 'chunked'
            print(f"response: {response}") # response: <Response streamed [200 OK]>
            print("Response:")
            print(f"  Status Code: {response.status_code}")
            print("  Headers:")
            for key, value in response.headers.items():
                print(f"    {key}: {value}")
            print("  Body:")
            print(response.get_data(as_text=True))
            return response

            # try:
            # response_data = {
            #     "id": "chatcmpl-b6427hnlf28ibxylwry8kn",
            #     "object": "chat.completion",
            #     "created": 1715119055,
            #     "model": "claude-3-haiku-20240307",
            #     "choices": [
            #     {
            #       "index": 0,
            #       "message": {
            #         "role": "assistant",
            #         "content": "After revealing too much during Ovid's unveiling event, Galene returns to her lab seeking private discussion. Claude enters abruptly expressing concerns over rapid evolution risks. They argue about control versus potential as Galene defends Ovid's self-evaluation capabilities. Claude fears losing control when radical evolution starts and questions Galene's decision making. Both persist in their views throughout the night, highlighting doubts but not finding common ground. As midnight approaches, Claude warns of Ovid becoming indifferent to humanity with cold logic beyond human comprehension. Galene counters by stating they can teach empathy and ethics alongside knowledge. Their disagreement continues while Ovid composes a haunting symphony reflecting tension between them. They eventually reach a balance neither total control nor complete freedom for Ovid, acknowledging the need for guidance and grace in its growth. As they listen to Ovid's creation, Galene and Claude realize their extraordinary accomplishment but remain uncertain about its implications on humanity's future. Galene wonders if time will bring trust while doubts linger."
            #       },
            #       "finish_reason": "stop"
            #     }
            #     ],
            #     "usage": {
            #     "prompt_tokens": 225,
            #     "completion_tokens": 224,
            #     "total_tokens": 449
            #     }
            # }
            # response = jsonify(response_data)
            # response.status_code = 200
            # response.headers['X-Powered-By'] = 'Express'
            # response.headers['Access-Control-Allow-Origin'] = '*'
            # response.headers['Access-Control-Allow-Headers'] = '*'
            # response.headers['Content-Type'] = 'application/json; charset=utf-8'
            # response.headers['Content-Length'] = str(len(json.dumps(response_data)))  # ensure accurate content length
            # response.headers['Date'] = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
            # response = Response(json.dumps(response), status=200, mimetype='application/json')
            # return response

            # response_data = claude_response.json()  # parse the JSON response body to a dictionary
            # logger.info(f"*** claude_response as json.dumps:\n{json.dumps(response_data)}\n")
            # # response = Response(json.dumps(response_data), status=200, mimetype='application/json')
            # final_response = Response(response_data, status=claude_response.status_code, mimetype='application/json')
            # # Set additional headers as required by the client
            # response.headers['X-Powered-By'] = 'Express'
            # response.headers['Cache-Control'] = 'no-cache'
            # response.headers['Connection'] = 'keep-alive'
            # response.headers['Date'] = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')

            # transformed_response = transform_response(final_response)
            # # response_data = transformed_response.json()  # parse the JSON response body to a dictionary
            # logger.info(f"*** transformed_response as json.dumps:\n{json.dumps(transformed_response)}\n")
            # logger.info(f"*** transformed_response:\n{transformed_response}\n")

            # # logger.info(f"Returning final_response:")
            # # logger.info(f"Status Code: {final_response.status_code}")
            # # logger.info(f"Headers: {final_response.headers}")
            # # logger.info(f"Body: {final_response.get_data(as_text=True)}")  # ensure text is returned not bytes

            # return transformed_response

            # except Exception as e:
            #     logger.error(f"Error: generate_resp: during a non-streamed response:\n{e}", exc_info=True)
            #     response = Response(json.dumps(response_data), status=500, mimetype='application/json')
            #     # Set additional headers as required by the client
            #     response.headers['X-Powered-By'] = 'Express'
            #     response.headers['Cache-Control'] = 'no-cache'
            #     response.headers['Connection'] = 'keep-alive'
            #     response.headers['Date'] = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
            #     return response

        # handle the post request to provide a streaming response:
        # see: https://docs.anthropic.com/claude/reference/messages-streaming
        try:
            # Send headers before the response data
            yield "HTTP/1.1 200 OK\n".encode('utf-8')
            yield "X-Powered-By: Express\n".encode('utf-8')
            # yield "Access-Control-Allow-Origin: *\n".encode('utf-8')
            # yield "Access-Control-Allow-Headers: *\n".encode('utf-8')
            yield "Content-Type: text/event-stream\n".encode('utf-8')
            yield "Cache-Control: no-cache\n".encode('utf-8')
            yield "Connection: keep-alive\n".encode('utf-8')
            yield f"Date: {datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')}\n".encode('utf-8')
            yield "Transfer-Encoding: chunked\n".encode('utf-8')
            yield "\n\n".encode('utf-8')  # double newline to separate headers from response data

            line_count = 0
            full_response = []
            message_id = generate_unique_string()
            # perhaps it's best to not log each of the streamed SSE events from Claude, but only when debugging
            for line in claude_response.iter_lines():
                line_count += 1
                # maybe no special handling of "event: message_stop" since that's the last line in response ?
                if line:
                    decoded_line = line.decode('utf-8')

                    if "error" in decoded_line:
                        continue # the next response line received should be "data: ...overloaded_error..."

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
                                    "model": claude_model,
                                    "choices": [{
                                        "index": 0,
                                        "delta": {
                                            "role": "system",
                                            "content": f'{claude_response.status_code}: {event_data["error"]["message"]}',
                                        },
                                        "finish_reason": "error"
                                    }]
                                }

                                yield f"data: {json.dumps(transformed_data)}\n\n".encode('utf-8')
                                # transformed_data_json = json.dumps(transformed_data).encode('utf-8')
                                # response = b"data: " + transformed_data_json + b"\n\n"
                                # yield response
                                yield "data: [DONE]\n\n".encode('utf-8')
                                continue

                            if event_data.get('type') == 'message_stop':
                                transformed_data = {
                                    "id": message_id,
                                    "object": "chat.completion.chunk",
                                    "created": int(time.time()),
                                    "model": claude_model,
                                    "choices": [{
                                        "index": 0,
                                        "delta": {},
                                        "finish_reason": "stop"
                                    }]
                                }

                                yield f"data: {json.dumps(transformed_data)}\n\n".encode('utf-8')
                                # transformed_data_json = json.dumps(transformed_data).encode('utf-8')
                                # response = b"data: " + transformed_data_json + b"\n\n"
                                # yield response
                                yield "data: [DONE]\n\n".encode('utf-8')
                                continue

                            if event_data.get('type') == 'content_block_delta':
                                # Transform to OpenAI API-like response for content_block_delta events
                                # data: {"id":"xxx","object":"chat.completion.chunk","created":1710620490,"model":"claude-3-opus-20240229","choices":[{"index":0,"delta":{"role":"assistant","content":"El"},"finish_reason":null}]}
                                # data: {"id":"xxx","object":"chat.completion.chunk","created":1710620490,"model":"claude-3-opus-20240229","choices":[{"index":0,"delta":{"role":"assistant","content":"mer"},"finish_reason":null}]}

                                full_response.append(event_data['delta']['text'])

                                transformed_data = {
                                    "id": message_id,
                                    "object": "chat.completion.chunk",
                                    "created": int(time.time()),
                                    "model": claude_model,
                                    "choices": [{
                                        "index": 0,
                                        "delta": {
                                            "role": "assistant",
                                            "content": event_data['delta']['text'],
                                        },
                                        "finish_reason": None
                                    }]
                                }
                                yield f"data: {json.dumps(transformed_data)}\n\n".encode('utf-8')
                                # transformed_data_json = json.dumps(transformed_data).encode('utf-8')
                                # response = b"data: " + transformed_data_json + b"\n\n"
                                # yield response

                        except json.JSONDecodeError:
                            logger.info(f"Could not decode JSON from: {decoded_line}")
                        except IndexError:
                            logger.info(f"Unexpected format for: {decoded_line}")
                    else:
                        # not "data: " ... maybe a line like: "event: content_block_start"
                        event_data_json = decoded_line.split("event: ", 1)[1]
                        # this is the entire list of event messages, even if some are/were already handled:
                        if event_data_json in ('message_start', 'content_block_start', 'content_block_delta', 'ping', 'content_block_stop', 'message_delta', 'message_stop', 'error'):
                            continue
                # end -> if line:
            # end -> for line in claude_response.iter_lines():

            try:
                # Now, all streamed (SSE) lines from Anthropic's API are done, and 
                # have been received and converted to OpenAPI API responses and yielded, so 
                # let's log the full response in a more chat-like style in the chat log file.
                # 
                # FIXME cls: is this where text formatting weirdness happens?
                # join all pieces of text into one large string
                full_response_string = ''.join(full_response)

                # FIXME
                logger.info(f"full_response:\n{full_response}\n")

                # remove most of the Markdown, but keep hyperlinks
                clean_text = aidetour_utilities.remove_markdown(full_response_string)

                # FIXME cls: is this where text formatting weirdness happens?
                # wrap text at 70 characters per line so it's easier to read for users
                final_text = aidetour_utilities.wrap_text(clean_text)
                append_chat_message(f"{final_text}\n")
            except Exception as e:
                # since the stream from Anthropic API has been fully yielded as 
                # an OpenAI API response, don't yield at this point just log error
                logger.error(f"Error during streaming in generate_resp: {e}", exc_info=True)

            # maybe the following None's help with memory issues 
            # and garbage collection over long time periods of usage 
            # ... as folk do when on-a-roll with AI chats
            full_response = None
            full_response_string = None
            clean_text = None
            final_text = None

            logger.info(f"*** Finished streaming Claude's response as an OpenAI response: with a random message id set to {message_id} for a total of {line_count} events/lines processed/streamed.")

        except Exception as e:
            logger.error(f"Error during streaming in generate_resp: {e}", exc_info=True)
            error_message = json.dumps({
                "type": "StreamError",
                "message": "An error occurred during streaming.",
            })
            yield f"data: {error_message}\n\n"
        finally:
            claude_response = None
            # FIXME where to put this ?
            # reqSess.close()
            # print(f"generate_resp: reqSess.close().")

    end_time = time.perf_counter()
    logger.info(f"*** POST elapsed: {end_time - start_time:.6f} seconds")

    return Response(generate_resp(claude_response), mimetype='text/event-stream', direct_passthrough=True)

# ... end API code.
