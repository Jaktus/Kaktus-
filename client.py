import socket
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
from datetime import datetime

class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("mo'sapp")
        self.running = False

        # GUI vorbereiten (wird später angezeigt)
        self.text_area = scrolledtext.ScrolledText(master, wrap=tk.WORD, state="disabled", height=20)
        self.entry = tk.Entry(master)
        self.sende_button = tk.Button(master, text="Senden", command=self.senden)

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            # Trage hier deine Server-IP ein
            self.client.connect(("192.168.178.86", 8000))
            print("line23")

        except Exception as e:
            messagebox.showerror("Verbindungsfehler", f"Verbindung zum Server fehlgeschlagen:\n{e}")
            self.master.destroy()
            return

        self.name_eingeben()

    def name_eingeben(self):
        self.name_fenster = tk.Toplevel(self.master)
        self.name_fenster.title("Name eingeben")
        self.name_fenster.grab_set()
        self.name_fenster.geometry("300x100")

        tk.Label(self.name_fenster, text="Wie heißt du?").pack(pady=10)
        self.name_entry = tk.Entry(self.name_fenster)
        self.name_entry.pack(padx=20)
        self.name_entry.bind("<Return>", self.bestätige_name)
        self.name_entry.focus()

        tk.Button(self.name_fenster, text="OK", command=self.bestätige_name).pack(pady=5)

    def bestätige_name(self, event=None):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Fehlender Name", "Bitte gib einen Namen ein.")
            return

        self.name = name
        self.name_fenster.destroy()

        # GUI aktivieren
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.entry.pack(padx=10, pady=(0, 10), fill=tk.X)
        self.entry.bind("<Return>", self.senden)
        self.sende_button.pack(padx=10, pady=(0, 10))

        self.running = True
        self.start_empfang_thread()

        # Willkommensnachricht senden
        self.sende_nachricht(f"{self.name} ist dem Chat beigetreten.")

    def sende_nachricht(self, text):
        try:
            self.client.send(text.encode("utf-8"))
        except Exception as e:
            messagebox.showerror("Sende-Fehler", f"Nachricht konnte nicht gesendet werden:\n{e}")
            self.beenden()

    def senden(self, event=None):
        nachricht = self.entry.get().strip()
        if not nachricht:
            return

        uhrzeit = datetime.now().strftime("[%H:%M]")
        text = f"{uhrzeit} {self.name}: {nachricht}"
        self.sende_nachricht(text)
        self.entry.delete(0, tk.END)

    def start_empfang_thread(self):
        empfang_thread = threading.Thread(target=self.empfange)
        empfang_thread.daemon = True
        empfang_thread.start()

    def empfange(self):
        while self.running:
            try:
                nachricht = self.client.recv(1024)
                if not nachricht:
                    break  # Verbindung wurde getrennt
                self.zeige_nachricht(nachricht.decode("utf-8"))
            except Exception as e:
                self.zeige_nachricht("[Fehler beim Empfangen]")
                break

        self.running = False
        self.client.close()
        self.master.quit()

    def zeige_nachricht(self, text):
        self.text_area.config(state="normal")
        self.text_area.insert(tk.END, text + "\n")
        self.text_area.yview(tk.END)
        self.text_area.config(state="disabled")

    def beenden(self):
        if self.running:
            self.running = False
            try:
                self.client.shutdown(socket.SHUT_RDWR)
                self.client.close()
            except:
                pass
        self.master.destroy()


def main():
    root = tk.Tk()
    client = ChatClient(root)
    root.protocol("WM_DELETE_WINDOW", client.beenden)
    root.mainloop()

if __name__ == "__main__":
    main()
