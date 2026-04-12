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
        Post = new records. Only accepts /bookmark/ without number as uses seq to add.
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
                        # Need to error check the the post content
                        # then insert it into the sequence
                        # Will attempt it first with clean curl command
                        length = int(self.headers.get("Content-Length"))
                        raw = self.rfile.read(length)
                        try:
                            raw_loaded = json.loads(raw)
                            # adding to my list
                            bookmark_dict[dict_index] = raw_loaded
                            self.send_response(200)

                            self.send_header("Content-type", "application/json")
                            basic_put_body = f"Completed PUT! \
                            The following was replaced at {dict_index}: "

                            full_put_body = basic_put_body + str(raw_loaded)
                            self.send_header("Content-Length", int(len(full_put_body)))
                            self.end_headers()
                            self.wfile.write(full_put_body.encode("utf-8"))

                        except json.JSONDecodeError as json_e:
                            print(f"JSONDecodeError: {json_e}")
                    except ValueError:
                        return None
                else:
                    self.send_error(400, "Your index does not exist in the endpoint")
            except ValueError as E:
                print(f"Value Error: {E}")

    # def do_PUSH(self):
    #     """
    #     Existing Records!!
    #     """
    #     if self.path == "/":
    #         basic_200_body = """
    #         Welcome to the api! You are at the root page,
    #         you cannot post anything from here
    #         """
    #         self.send_response(200)
    #         self.send_header("Content-type", "application/json")
    #         self.send_header("Content-Length", int(len(basic_200_body)))
    #         self.end_headers()
    #         self.wfile.write(basic_200_body.encode("utf-8"))

    #     elif self.path.startswith("/bookmark/"):
    #         route_number_split = self.path.split("/")
    #         try:
    #             dict_index = int(route_number_split[2])
    #             if dict_index in bookmark_dict.keys():
    #                 try:
    #                     # Need to error check the the post content
    #                     # then insert it into the sequence
    #                     # Will attempt it first with clean curl command
    #                     length = int(self.headers.get("Content-Length"))
    #                     raw = self.rfile.read(length)
    #                     try:
    #                         raw_loaded = json.loads(raw)
    #                         # adding to my list
    #                         bookmark_dict[_SEQ] = raw_loaded
    #                         _SEQ = _SEQ + 1

    #                     except json.JSONDecodeError as json_e:
    #                         print(f"JSONDecodeError: {json_e}")
    #                 except ValueError:
    #                     return None
    #         except ValueError as E:
    #             print(f"Value Error: {E}")


with HTTPServer(addr, MyHandler) as serverr:
    serverr.serve_forever()
