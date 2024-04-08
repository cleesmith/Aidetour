import socket

def check_if_listening(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
            print(f"Success: The application is listening on {host}:{port}.")
        except socket.error as err:
            print(f"Failure: No application is listening on {host}:{port}. Error: {err}")

if __name__ == "__main__":
    HOST = '127.0.0.1'  # The server's hostname or IP address
    PORT = 5600         # The port used by the server
    check_if_listening(HOST, PORT)
