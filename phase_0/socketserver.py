import socketserver


class myTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        pieces = [b""]
        total = 0
        while b"\n" not in pieces[-1] and total < 10_000:
            pieces.append(self.request.recv(2000))
            total += len(pieces[-1])
        self.data = b"".join(pieces)
        print(f"recieved from {self.client_address[0]}:")
        print(self.data.decode("utf-8"))

        # sending data back just uppercase
        self.request.sendall(self.data.upper())  # I assume it will close on its own?


def serversock():
    addr = "localhost", 9000
    with socketserver.TCPServer(addr, myTCPHandler) as server:
        server.serve_forever()


if __name__ == "__main__":
    serversock()
