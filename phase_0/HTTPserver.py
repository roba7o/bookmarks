from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

local_path = Path(__file__).parent
addr = "localhost", 9000

list_var_module_level = []

# TODO -> handle requests better with json.dumps and jsonloads


class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.lower() == "/about":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"This is a server you have just called!\n")

        elif self.path.lower() == "/robert":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Yep my name!\n")

        elif self.path.lower() == "/document":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            with open(local_path / "phase_0.html", "r") as file:
                self.wfile.write(file.read(5096).encode())

        elif self.path.lower() == "/bookmark":
            print("MyServer: I got a GET request")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(list_var_module_level.encode())

    def do_POST(self):
        if self.path.lower() == "/bookmark":
            print("MyServer: I got a POST request")

            content_length = int(self.headers["Content-Length"])
            print(f"Content data length is {content_length}")

            data = self.rfile.read()
            list_var_module_level.append(data)
            self.send_response(201)

        else:
            self.send_error(404)


with HTTPServer(addr, MyHandler) as serverr:
    serverr.serve_forever()
