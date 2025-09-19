import socket

def aktion():

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #IP-Adresse und port
    server_ip = "127.0.0.1"
    server_port = 8000

    client.connect((server_ip, server_port))

    while True:
        nachricht = input("Nachricht: ")

        client.send(nachricht.encode("utf-8")[:1024])

aktion()