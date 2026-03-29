from http.server import BaseHTTPRequestHandler, HTTPServer

addr = "localhost", 9000


class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Hello There\n")


with HTTPServer(addr, MyHandler) as serverr:
    serverr.serve_forever()
