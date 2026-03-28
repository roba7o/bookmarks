from socket import AF_INET, SHUT_WR, SOCK_STREAM, socket


def create_server():
    server_socket = socket(AF_INET, SOCK_STREAM)
    try:
        server_socket.bind(("127.0.0.1", 9000))
        server_socket.listen(5)
        while True:
            conn, addr = server_socket.accept()
            data_rec = conn.recv(4096).decode()
            data_rec = data_rec.split("\n")
            if len(data_rec) > 0:
                print(f"printing request {data_rec}")

            body = "<html><body>Hello World</body></html>\r\n\r\n"
            body_length = len(body.encode("utf-8"))

            headers = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html; charset=utf-8\r\n"
                f"Content-Length: {body_length}\r\n"
                "\r\n"
            )

            conn.sendall(headers.encode() + body.encode())
            conn.shutdown(
                SHUT_WR
            )  # this tells the kernel im done SENDING on this connection.

    except KeyboardInterrupt:
        print("\nShuttingDown...\n")
    except Exception as e:
        print(f"Error: {e}")
    server_socket.close()


print("Access http://127.0.0.1:9000")
create_server()
