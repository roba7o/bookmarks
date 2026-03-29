from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

local_path = Path(__file__).parent
addr = "localhost", 9000


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
                self.wfile.write(file.read().encode())

        else:
            self.send_error(404)


with HTTPServer(addr, MyHandler) as serverr:
    serverr.serve_forever()
