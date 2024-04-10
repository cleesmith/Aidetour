import shelve
import os

def load_settings():
    app_folder = os.path.dirname(os.path.abspath(__file__))
    settings_file = os.path.join(app_folder, 'Aidetour_Settings')
    settings = shelve.open(settings_file)
    
    api_key = settings.get('api_key', '')
    host = settings.get('host', '')
    port = settings.get('port', '')
    
    settings.close()
    
    return api_key, host, port

def save_settings(api_key, host, port):
    app_folder = os.path.dirname(os.path.abspath(__file__))
    settings_file = os.path.join(app_folder, 'Aidetour_Settings')
    settings = shelve.open(settings_file)
    
    settings['api_key'] = api_key
    settings['host'] = host
    settings['port'] = int(port)
    
    settings.close()

# Example usage in the CLI app
if __name__ == '__main__':
    api_key, host, port = load_settings()
    
    print(f"Aidetour Settings:")
    print(f"Anthropic API Key: {api_key}")
    print(f"Host: {host}")
    print(f"Port: {port}")
    
    # Prompt the user for new settings
    new_api_key = input("Enter new Anthropic API Key (leave blank to keep current): ")
    new_host = input("Enter new Host (leave blank to keep current): ")
    new_port = input("Enter new Port (leave blank to keep current): ")
    
    # Update the settings if new values are provided
    if new_api_key:
        api_key = new_api_key
    if new_host:
        host = new_host
    if new_port:
        port = new_port
    
    save_settings(api_key, host, port)
    print("Settings updated successfully.")

