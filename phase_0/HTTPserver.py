from http.server import BaseHTTPRequestHandler, HTTPServer

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

        else:
            self.send_error(404)


with HTTPServer(addr, MyHandler) as serverr:
    serverr.serve_forever()
