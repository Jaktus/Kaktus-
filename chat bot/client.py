import socket


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("192.168.178.200", 12346))
client.settimeout(0.1)

print("Verbündung mit dem Server wurde hergestellt,Kamerad.")


wie_jeder_will = "M0nke"

while True:
    nachricht = input("\033[32m" + wie_jeder_will + "\033[0m" + ":")
    nachricht = "\033[32m" + wie_jeder_will + "\033[0m" + ": " + "\033[33m" + nachricht + "\033[0m"
    client.send(nachricht.encode("utf-8"))

    while True:
        try:

            antwort = client.recv(1024).decode("utf-8")
            print(antwort + "\n")
        except socket.timeout:

            break
        except:
            print("Tote hose:(")
            client.close()

            exit()

client.close()
