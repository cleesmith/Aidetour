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
- A chat log of your requests and the Claude's responses.
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

4. Set up the configuration files:
   - Update the `.env` file with your Anthropic API key.
   - Configure the server settings (host and port) in the `config.ini` file.
   - Optionally, update the `models.ini` file with details about Claude's different models.

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

The application will start with a system tray icon. Right-click on the icon to access the menu options:
- Info: Displays the server's listening address and port.
- Models: Shows the available Claude models.
- Logs: Opens the application log file.
- Exit: Quits the application.

### CLI Mode

To run Aidetour in CLI mode, use the `--cli` flag:
```
python Aidetour.py --cli
```

The application will start the Flask server and listen for incoming requests.

## Configuration

- `.env`: Set your Anthropic API key in this file.
- `config.ini`: Configure the server settings (host and port) in this file.
- `models.ini`: Update this file with details about Claude's different models.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, 
please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

## Acknowledgements

- [Python](https://www.python.org/)
- [Flask](https://flask.palletsprojects.com/)
- [Rumps](https://github.com/jaredks/rumps)
- [wxPython](https://www.wxpython.org/)
- [Anthropic Claude API](https://www.anthropic.com/)
- [OpenAI API](https://openai.com/)

