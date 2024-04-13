# aidetour_api_handler

import os
import sys
import socket
import errno
import subprocess
from loguru import logger
import signal
import argparse
import time
import uuid
import logging
import json
import configparser
import subprocess
import threading
from threading import Event
from datetime import datetime, timezone

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
"""
# API Flask Anthropic related:
import requests
from waitress import serve, task, create_server
from flask import Flask, Response, jsonify, request, stream_with_context, make_response
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
import anthropic

# Aidetour modules:
import aidetour_logging
import aidetour_utilities
from aidetour_utilities import APP_NAME, APP_LOGO
from aidetour_utilities import HOST, PORT
from aidetour_utilities import ANTHROPIC_API_KEY, ANTHROPIC_API_MODELS


MAX_TOKENS = 100
TEMPERATURE = 1
STREAM_RESPONSE = True
ANTHROPIC_MESSAGES_API_URL = 'https://api.anthropic.com/v1/messages'
DEFAULT_MODEL = "claude-3-haiku-20240307"
# ANTHROPIC_API_KEY = None
# MODELS_DATA = None


flask_app = Flask(__name__)
# Enable CORS for all routes and origins
CORS(flask_app, resources=r'/v1/*', supports_credentials=True)

# cls: these break typical logger.info, so only use for debugging:
# flask_app.logger.setLevel(logging.DEBUG)
# logging.getLogger('flask_cors').level = logging.DEBUG


def run_flask_app():
    print(f"run_flask_app: aidetour_utilities.load_settings()={aidetour_utilities.load_settings()}")
    aidetour_utilities.load_settings()
    print(f"run_flask_app: ANTHROPIC_API_MODELS={ANTHROPIC_API_MODELS}")
    # global ANTHROPIC_API_KEY
    # ANTHROPIC_API_KEY = key
    # global MODELS_DATA
    # MODELS_DATA = aidetour_utilities.load_models_data()
    try:
        logger.info(f"run_flask_app: host={HOST} port={PORT}")
        serve(flask_app, host=HOST, port=PORT)
    except OSError as e:
        if e.errno == errno.EADDRINUSE:
            logger.info(f"Error: Address {HOST}:{PORT} is already in use.")

def generate_unique_string():
    unique_id = str(uuid.uuid4())
    unique_id = unique_id.replace("-", "")
    unique_id = unique_id[:24]
    unique_string = "msg_" + unique_id
    logger.info(f"generate_unique_string: {unique_string}")
    return unique_string

def get_openai_request_data(openai_request):
    claude_data = {
        "model": openai_request.get("model", DEFAULT_MODEL),
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

# Function to create a consistent error response format
def create_error_response(error_type, message, status_code):
    error_response = json.dumps({
        "type": "error",
        "error": {
            "type": error_type,
            "status_code": status_code,  # Include the actual status code
            "message": message
        }
    })
    return Response(error_response, status=status_code, mimetype='application/json')


# start API code ...

# raise an error, like bad route, for testing only
# @flask_app.route('/cause_exception')
# def cause_exception():
#     raise Exception("*** exception raised by: /cause_exception ***")

# Error handler for HTTP exceptions
@flask_app.errorhandler(HTTPException)
def handle_http_exception(e):
    response = e.get_response()
    # Log the error using the configured logger
    logger.error(f"HTTPException handled by handle_http_exception: {e.description}", exc_info=True)
    response.data = jsonify({
        "type": e.name,
        "message": e.description,
    }).data
    response.content_type = "application/json"
    return response

# Error handler for non-HTTP exceptions (catch-all)
@flask_app.errorhandler(Exception)
def handle_exception(e):
    # Log the error using the configured logger
    logger.error(f"Exception handled by handle_exception: {e}", exc_info=True)
    return jsonify({
        "type": "InternalServerError",
        "message": "An unexpected error has occurred.",
    }), 500

@flask_app.route('/v1/shutdown', methods=['POST'])
def shutdown():
    logger.info("Received shutdown request")
    return 'Server shutting down...'

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
    return jsonify(ANTHROPIC_API_MODELS)

@flask_app.route('/v1/chat/completions', methods=['OPTIONS'])
def chat_completions_options():
    # note: if not using CORS(app) the following are required:
    # response = make_response()
    # response.headers.add('Access-Control-Allow-Origin', 'https://app.novelcrafter.com')
    # response.headers.add('Access-Control-Allow-Headers', '*')
    # response.headers.add('Access-Control-Allow-Methods', 'PUT, POST, PATCH, DELETE, GET')
    # return response
    return '', 200

@flask_app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    start_time = time.perf_counter()
    logger.info("\n\nIncoming OpenAI API POST request to: '/v1/chat/completions'")

    oai_data = request.get_json()
    if oai_data is None:
        logger.info("\n400: error: Invalid JSON payload")
        # FIXME = will this work with novelcrafter ?
        return jsonify({'error': 'Invalid JSON payload'}), 400
    logger.info(f"oai_data: {oai_data}")
    
    claude_data = get_openai_request_data(oai_data)
    logger.info("\n\nConverted OpenAI API data to Claude API data:")
    logger.info(json.dumps(claude_data, indent=2))
    claude_model = claude_data["model"]

    headers = {
        "anthropic-version": "2023-06-01",
        "anthropic-beta": "messages-2023-12-15",
        "content-type": "application/json",
        "x-api-key": ANTHROPIC_API_KEY,
    }

    keys_of_interest = ["anthropic-version", "anthropic-beta"]
    headers_to_print = ", ".join(f"{key}: {headers[key]}" for key in keys_of_interest if key in headers)

    # ************* post/send to Claude 3
    claude_response = requests.post(ANTHROPIC_MESSAGES_API_URL, headers=headers, data=json.dumps(claude_data), stream=STREAM_RESPONSE)
    # *************
    logger.info(f"\nPOST to URL: '{ANTHROPIC_MESSAGES_API_URL}' headers: '{headers_to_print}'")
    logger.info(f">>> claude's response: {claude_response}")

    if claude_response.status_code != 200:
        try:
            error_info = claude_response.json()
            detailed_message = error_info.get('message', 'No detailed message provided.')
        except ValueError:
            detailed_message = 'Response was not in JSON format.'
        error_mappings = {
            401: ("authentication_error", "There's an issue with your API key.\n Quit the app Aidetour and check your settings"),
            403: ("permission_error", "Your API key does not have permission to use the specified resource."),
            404: ("not_found_error", "The requested resource was not found."),
            429: ("rate_limit_error", "Your account has hit a rate limit."),
            500: ("api_error", "An unexpected error has occurred internal to Anthropic's systems."),
            529: ("overloaded_error", "Anthropic's API is temporarily overloaded, try again later.")
        }
        error_type, default_message = error_mappings.get(
            claude_response.status_code, 
            ("unexpected_error", f"An unexpected error occurred with status code {claude_response.status_code}.")
        )
        error_message = detailed_message if detailed_message != 'No detailed message provided.' else default_message
        logger.error(f"Error calling Anthropic API: Status code {claude_response.status_code}, Message: {error_message}")
        return create_error_response(error_type, error_message, claude_response.status_code)

    def generate_resp(claude_response):
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
            yield "\n\n".encode('utf-8')  # Double newline to separate headers from response data

            line_count = 0
            message_id = generate_unique_string()
            # perhaps it's best to not log each of the streamed SSE events from Claude, but only when debugging
            for line in claude_response.iter_lines():
                line_count += 1
                # maybe no special handling of "event: message_stop" since that's the last line in response ?
                if line:
                    decoded_line = line.decode('utf-8')

                    if "error" in decoded_line:
                        # from: Anthropic API error events:
                        # We may occasionally send errors in the event stream. 
                        # For example, during periods of high usage, you may receive an overloaded_error, 
                        # which would normally correspond to an HTTP 529 in a non-streaming context:
                        # event: error
                        # data: {"type": "error", "error": {"type": "overloaded_error", "message": "Overloaded"}}
                        #
                        # https://community.openai.com/t/status-code-503-that-model-is-currently-overloaded-with-other-requests/31433
                        # OpenAI API status code 503
                        # {
                        #   "error": {
                        #     "message": "That model is currently overloaded with other requests. You can retry your request, or contact us through our help center at help.openai.com if the error persists. (Please include the request ID 7ef84fe5909aa6768fb8d39a081a5ccc in your message.)",
                        #     "type": "server_error",
                        #     "param": null,
                        #     "code": null
                        #   }
                        # }
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
                                yield "data: [DONE]\n\n".encode('utf-8') # cls? is this needed?
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
                                yield "data: [DONE]\n\n".encode('utf-8')
                                continue

                            if event_data.get('type') == 'content_block_delta':
                                # Transform to OpenAI API-like response for content_block_delta events
                                # data: {"id":"xxx","object":"chat.completion.chunk","created":1710620490,"model":"claude-3-opus-20240229","choices":[{"index":0,"delta":{"role":"assistant","content":"El"},"finish_reason":null}]}
                                # data: {"id":"xxx","object":"chat.completion.chunk","created":1710620490,"model":"claude-3-opus-20240229","choices":[{"index":0,"delta":{"role":"assistant","content":"mer"},"finish_reason":null}]}
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

            logger.info(f"Finished streaming Claude's response as an OpenAI response: with a random message id set to {message_id} for a total of {line_count} events/lines processed/streamed.")

        except Exception as e:
            logger.error(f"Error during streaming in generate_resp: {e}", exc_info=True)
            error_message = json.dumps({
                "type": "StreamError",
                "message": "An error occurred during streaming.",
            })
            yield f"data: {error_message}\n\n"

    end_time = time.perf_counter()
    logger.info(f"POST elapsed: {end_time - start_time:.6f} seconds")

    return Response(generate_resp(claude_response), mimetype='text/event-stream', direct_passthrough=True)
    # note: the original non-streamed approach:
    # response = Response(generate_resp(claude_response), mimetype='text/event-stream')
    # response.headers['X-Powered-By'] = 'Express'
    # response.headers['Access-Control-Allow-Origin'] = '*'
    # response.headers['Access-Control-Allow-Headers'] = '*'
    # response.headers['Cache-Control'] = 'no-cache'
    # response.headers['Connection'] = 'keep-alive'
    # response.headers['Date'] = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    # response.headers['Transfer-Encoding'] = 'chunked'
    # return response

# ... end API code.
