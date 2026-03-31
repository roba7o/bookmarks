import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

local_path = Path(__file__).parent
addr = "localhost", 9000


# TODO -> handle requests better with json.dumps and jsonloads
# plan: post, get, put, delete -> fixed list of vars with indents, 1,2 with starter at 3
# first just going to get and post working without numbers

bookmark_dict = {
    1: {"book": "Designing Data Intensive Applications", "Page": 88},
    2: {"book": "Fluent Python", "Page": 444},
    3: {"book": "Version Control with Git", "Page": "144"},
}


class MyHandler(BaseHTTPRequestHandler):
    number_in_memory = 4

    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b"Welcome to the api!")

        elif self.path == "/bookmark/":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(bookmark_dict).encode("utf-8"))

        else:
            self.send_error(404, "Not Found!")

    def do_POST(self):
        if self.path == "/bookmark/":
            content_length = int(self.headers.get("Content-length", 0))
            body = self.rfile.read(content_length)

            try:
                data = json.loads(body)
                # normally would process the data
                print(data)
                bookmark_dict[MyHandler.number_in_memory] = data
                MyHandler.number_in_memory += 1
                self.send_response(201, "It uploaded -> try a get")
            except json.JSONDecodeError:
                self.send_error(400, "not allowed mate")
        else:
            self.send_error(404, "Not Found mate!")


with HTTPServer(addr, MyHandler) as serverr:
    serverr.serve_forever()
