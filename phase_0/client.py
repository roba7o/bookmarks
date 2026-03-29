import socket

mysock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# kernel will allocate socket struct and pick a file descriptor (int)
# our params here tell the kernel what type of stuct to build in its internal memory

mysock.connect(("127.0.0.1", 9000))  # TCP ESTABLISHED
cmd = "GET lower/ HTTP/1.0\r\n\r\n".encode()  # METHOD PATH VERSION
mysock.send(cmd)

while True:
    data = mysock.recv(512)
    if len(data) > 1:
        print(data.decode(), end="")
    else:
        break

mysock.close()
