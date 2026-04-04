import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

local_path = Path(__file__).parent
addr = "localhost", 9000

# ======= Memory Variables =======

bookmark_dict = {
    1: {"book": "Designing Data Intensive Applications", "Page": 88},
    2: {"book": "Fluent Python", "Page": 444},
    3: {"book": "Version Control with Git", "Page": "144"},
}

_SEQ = 4


class MyHandler(BaseHTTPRequestHandler):
    global _SEQ

    def do_GET(self):
        if self.path == "/":
            basic_200_body = "Welcome to the api!"
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Content-Length", int(len(basic_200_body)))
            self.end_headers()
            self.wfile.write(basic_200_body.encode("utf-8"))

        elif self.path == "/bookmark/1":
            print(f"range check {range(1, _SEQ)}")
            route_number_split = self.path.split("/")
            dict_index = int(route_number_split[2])
            if dict_index not in range(1, _SEQ):
                self.send_error("400", "Index doesnt count")

            else:
                body = json.dumps(bookmark_dict[dict_index])
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Content-length", int(len(body)))
                self.end_headers()
                self.wfile.write(body.encode("utf-8"))

        else:
            self.send_error(404, "Not Found!")

    # def do_POST(self):
    #     if self.path == "/bookmark/":
    #         content_length = int(self.headers.get("Content-length", 0))
    #         body = self.rfile.read(content_length)

    #         try:
    #             data = json.loads(body)
    #             # normally would process the data
    #             print(data)
    #             bookmark_dict[MyHandler.number_in_memory] = data
    #             MyHandler.number_in_memory += 1
    #             self.send_response(201, "It uploaded -> try a get")
    #         except json.JSONDecodeError:
    #             self.send_error(400, "not allowed mate")
    #     else:
    #         self.send_error(404, "Not Found mate!")


with HTTPServer(addr, MyHandler) as serverr:
    serverr.serve_forever()
