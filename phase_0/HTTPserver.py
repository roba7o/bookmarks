import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

local_path = Path(__file__).parent
addr = "localhost", 9000

list_var_module_level = [{"book": "Designing Data Intensive Applications", "Page": 88}]

# TODO -> handle requests better with json.dumps and jsonloads


class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.lower() == "/bookmark":
            print("MyServer: I got a GET request")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            data_dumped = json.dumps(list_var_module_level)
            self.wfile.write(data_dumped.encode())

        else:
            self.send_error(404)

    def do_POST(self):
        if self.path.lower() == "/bookmark":
            print("MyServer: I got a POST request")

            content_length = int(self.headers["Content-Length"])
            print(f"Content data length is {content_length}")

            data = self.rfile.read()
            data_loaded = json.loads(data)
            list_var_module_level.append(data_loaded)
            self.send_response(201)

        else:
            self.send_error(404)


with HTTPServer(addr, MyHandler) as serverr:
    serverr.serve_forever()
