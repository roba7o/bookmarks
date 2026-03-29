import socketserver


class echoUpperHandler(socketserver.StreamRequestHandler):
    """
    StreamRequest will deal with
    - setup(): attache rfile and wfile to self
    - finish(): handles connection closing

    I redefine handle as i want to process rfile and wfile
    """

    def handle(self):
        print(self.client_address)
        data = self.rfile.readline().rstrip()
        data += b"\n\n<html><body>Hello World</body></html>\r\n\r\n"
        self.wfile.write(data.upper())


def serversock():
    addr = "localhost", 9000
    """
    class TCPServer(BaseServer) instantiates like such:
    def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True)

    # All other params i had to define in other project are here!
    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    request_queue_size = 5
    allow_reuse_address = False
    allow_reuse_port = False

    """
    with socketserver.TCPServer(addr, echoUpperHandler) as server:
        server.serve_forever()


if __name__ == "__main__":
    serversock()
