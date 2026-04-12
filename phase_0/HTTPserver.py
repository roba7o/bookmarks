import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

local_path = Path(__file__).parent
addr = "localhost", 9000


"""
Example Curl Command:
curl -v -X PUT localhost:9000/bookmark/1 -d '{"book": "desisiningggg", "Page": 555}'

"""

# ======= Memory Variables =======

bookmark_dict = {
    1: {"book": "Designing Data Intensive Applications", "Page": 88},
    2: {"book": "Fluent Python", "Page": 444},
    3: {"book": "Version Control with Git", "Page": "144"},
}

_SEQ = 4


class MyHandler(BaseHTTPRequestHandler):
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
                        print(f"JSONDecodeError: {json_e}")
                else:
                    return self.send_error(404, "Index out of range")
            except ValueError as E:
                print(f"Value Error: {E}")

    def do_PUT(self):
        """
        PUT will use sttarts with! -> and changes an existing key.
        """
        if self.path == "/":
            basic_200_body = """
            Welcome to the api! You can't do anything here with your
            request. You will need to add /bookmark/ to your endpoint.
            """
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
                        length = int(self.headers.get("Content-Length"))
                        raw = self.rfile.read(length)
                        try:
                            raw_loaded = json.loads(raw)
                            # adding to my list
                            bookmark_dict[dict_index] = raw_loaded
                            self.send_response(200)

                            self.send_header("Content-type", "application/txt")
                            basic_put_body = f"Completed PUT! \
                            The following was replaced at {dict_index}: "

                            full_put_body = basic_put_body + str(raw_loaded)
                            self.send_header("Content-Length", int(len(full_put_body)))
                            self.end_headers()
                            self.wfile.write(full_put_body.encode("utf-8"))

                        except json.JSONDecodeError as json_e:
                            self.send_error(400, f"JSONDecodeError: {json_e}")
                    except ValueError as val_e:
                        self.send_error(400, f"value error: {val_e}")
                else:
                    self.send_error(404, "Resource not found in the endpoint")
            except ValueError as E:
                print(f"Value Error: {E}")

    def do_POST(self):
        """
        New entries! Need to use the global sequencer!
        """
        if self.path == "/":
            basic_200_body = """
            Welcome to the api! You can't do anything here with your
            request. You will need to add /bookmark/new_book to your endpoint.
            """
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Content-Length", int(len(basic_200_body)))
            self.end_headers()
            self.wfile.write(basic_200_body.encode("utf-8"))

        elif self.path == ("/bookmark/new_book"):
            try:
                length = int(self.headers.get("Content-Length"))
                raw = self.rfile.read(length)
                try:
                    raw_loaded = json.loads(raw)
                    # adding to my list
                    global _SEQ
                    _SEQ = _SEQ + 1
                    bookmark_dict[_SEQ] = raw_loaded
                    self.send_response(201)

                    self.send_header("Content-type", "application/txt")
                    basic_put_body = f"Completed POST! \
                    The following was added at {_SEQ}: "

                    full_put_body = basic_put_body + str(raw_loaded)
                    self.send_header("Content-Length", int(len(full_put_body)))
                    self.end_headers()
                    self.wfile.write(full_put_body.encode("utf-8"))

                except json.JSONDecodeError as json_e:
                    self.send_error(400, f"JSONDecodeError: {json_e}")
            except ValueError as val_e:
                self.send_error(400, f"value error: {val_e}")

    def do_DELETE(self):
        """
        DELETE will delete... an existing key!
        """
        if self.path == "/":
            basic_200_body = """
            Welcome to the api! You can't do anything here with your
            request. You will need to add /bookmark/ to your endpoint.
            """
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
                        bookmark_dict.pop(dict_index)
                        self.send_response(200)
                        self.send_header("Content-type", "application/txt")
                        basic_delete_body = f"Completed DELETE! \
                        The following was deleted at {dict_index}: "
                        self.send_header("Content-Length", int(len(basic_delete_body)))
                        self.end_headers()
                        self.wfile.write(basic_delete_body.encode("utf-8"))
                    except ValueError as val_e:
                        self.send_error(400, f"value error: {val_e}")
                else:
                    self.send_error(404, "Resource not found in the endpoint")
            except ValueError as E:
                print(f"Value Error: {E}")


with HTTPServer(addr, MyHandler) as serverr:
    serverr.serve_forever()
