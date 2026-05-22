import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("192.168.178.200", 12345))
server.listen()

print("Server started.Warte auf clients...")

client_list = []

while True:
    client, address =server.accept()
    client_list.append(client)

    for c in client_list:
        try:
            c.settimeout(0.1)
            nachricht = c.recv(1024).decode("utf-8")
            if nachricht:
                print(nachricht)
                for other_client in client_list:
                    other_client.sendall(nachricht.encode("utf-8"))

        except:
            pass

server.close()
print("nikis server für dich")    

