# Aidetour

Aidetour is a Python application that acts as a middleman between the OpenAI API 
and the Anthropic Claude API. It translates requests intended for the OpenAI system 
into properly formatted Anthropic API requests, sends them to the Anthropic API, and 
then converts the responses back into OpenAI API-formatted streamed responses. The
app does not actually use an OpenAI API key, instead it uses your Anthropic API key 
which is required.

## Features

- Seamless integration between OpenAI API and Anthropic Claude API
- Support for multiple Claude models (e.g., Claude-3-Opus, Claude-3-Sonnet, Claude-3-Haiku)
- Graphical user interface (GUI) for both macOS and Windows
- Command-line interface (CLI) mode for terminal usage
- A chat log of your requests and Claude's responses, as pairs of "Me:" and "AI:"
- Logging functionality for tracking application events and errors

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/Aidetour.git
   ```

2. Navigate to the project directory:
   ```
   cd Aidetour
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### GUI Mode

- For macOS, run:
  ```
  python Aidetour.py
  ```

- For Windows, run:
  ```
  python Aidetour.py
  ```

The application will start with a system tray icon. 
Right-click on the systray (menu bar) icon to access the menu options:
- Status: Pings the local API server displays its status, as well as any other messages.
- Settings: To change the local API server's listening IP and port, your Anthropic API key, a list of available Claude 3 models.
- Log: Opens the app log file.
- Video: Opens a YouTube video about Aidetour.
- Quit: Quits the application.

### CLI Mode

To run Aidetour in CLI mode, use the `--cli` flag:
```
python Aidetour.py --cli
```

The application will start the API server and listen for incoming requests.

## Configuration


## Contributing

If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

## Acknowledgements

- [Anthropic Claude API](https://www.anthropic.com/)
- [OpenAI API](https://openai.com/)
- [Python](https://www.python.org/)
- [wxPython](https://www.wxpython.org/)
- [Flask](https://flask.palletsprojects.com/)
- [Flask_Cors](https://flask-cors.readthedocs.io/en/latest/)
- [Waitress](https://docs.pylonsproject.org/projects/waitress/en/latest/)
- [Requests](https://requests.readthedocs.io/en/latest/)
- [loguru](https://github.com/Delgan/loguru)
- [langchain_community](https://github.com/langchain-ai/langchain)
- [Pillow](https://python-pillow.org/)

