import json
import sys


def print_usage():
    print("Command line JSON database editor")
    print("Usage:")
    print("  python cli_json_editor.py <filename> <<<-- do not append '.json'")
    print("Commands:")
    print("  view   - View all keys and values")
    print("  get <key> - Get a value for a key")
    print("  set <key> <value> - Set a value for a key")
    print("  delete <key> - Delete a key and its value")
    print("  exit   - Exit the editor")

def load_data(filename):
    try:
        with open(filename + '.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_data(filename, data):
    with open(filename + '.json', 'w') as file:
        json.dump(data, file)

def main():
    if len(sys.argv) != 2:
        print("Error: Filename required")
        print_usage()
        sys.exit(1)
    
    filename = sys.argv[1]
    data = load_data(filename)
    print("Opened database:", filename)
    print_usage()
    
    while True:
        try:
            cmd = input("Enter command: ").strip().split()
            if not cmd:
                continue
            elif cmd[0] == 'exit':
                break
            elif cmd[0] == 'view':
                for key, value in data.items():
                    print(f"{key}: {value}")
            elif cmd[0] == 'get' and len(cmd) > 1:
                key = cmd[1]
                print(data.get(key, "Key not found"))
            elif cmd[0] == 'set' and len(cmd) > 2:
                key, value = cmd[1], ' '.join(cmd[2:])
                data[key] = value
                print(f"Set {key} to {value}")
            elif cmd[0] == 'delete' and len(cmd) > 1:
                key = cmd[1]
                if key in data:
                    del data[key]
                    print(f"Deleted {key}")
                else:
                    print("Key not found")
            else:
                print("Invalid command")
                print_usage()
        except Exception as e:
            print("Error:", e)
    
    save_data(filename, data)
    print("Database saved and closed")

if __name__ == "__main__":
    main()
