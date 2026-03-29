import socketserver


class echoUpperHandler(socketserver.StreamRequestHandler):
    def handle(self):
        data = self.rfile.readline().rstrip()
        data += "\n\n<html><body>Hello World</body></html>\r\n\r\n".encode()
        self.wfile.write(data.upper())


def serversock():
    addr = "localhost", 9000
    with socketserver.TCPServer(addr, echoUpperHandler) as server:
        server.serve_forever()


if __name__ == "__main__":
    serversock()
