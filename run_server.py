import sys
from aidetour_api_handler import run_flask_app

if __name__ == '__main__':
    host = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5600
    api_key = sys.argv[3] if len(sys.argv) > 3 else 'your_api_key'
    server_status = sys.argv[4] if len(sys.argv) > 4 else 'status'

    run_flask_app(host, port, api_key, server_status)
