import socket

def aktion():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_ip = "127.0.0.1"
    server_port = 8000

    server.bind((server_ip, server_port))

    server.listen(0)

    client_socket, client_address = server.accept()

    while True:
        nachricht = client_socket.recv(1024)

        nachricht = str(nachricht.decode(encoding="utf-8"))

        print(nachricht)

aktion()