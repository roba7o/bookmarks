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
            basic_200_body = "Welcome to the api! You are at the root page"
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Content-Length", int(len(basic_200_body)))
            self.end_headers()
            self.wfile.write(basic_200_body.encode("utf-8"))

        elif self.path.startswith("/bookmark/"):
            route_number_split = self.path.split("/")
            try:
                dict_index = int(route_number_split[2])
                if dict_index in bookmark_dict.keys():
                    try:
                        body = bookmark_dict[dict_index]
                        body_json = str(json.dumps(body))
                        self.send_response(200)
                        self.send_header("Content-type", "application/json")
                        self.send_header("Content-length", int(len(body_json)))
                        self.end_headers()
                        self.wfile.write(body_json.encode("utf-8"))
                    except json.JSONDecodeError as json_e:
                        print(f"jsondecode error as {json_e}")
                else:
                    return self.send_error(400, "Index out of range")
            except TypeError as E:
                print(f"Type error is: {E}")

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
