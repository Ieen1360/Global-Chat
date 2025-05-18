import tkinter as tk
from tkinter import scrolledtext, messagebox
import requests
import hashlib

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Global Simples")
        self.server_url = "http://localhost:5000"
        self.user_id = None
        self.setup_login()

    def setup_login(self):
        self.clear_window()
        tk.Label(self.root, text="Email:").pack()
        self.email_entry = tk.Entry(self.root)
        self.email_entry.pack()
        
        tk.Label(self.root, text="Senha:").pack()
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()
        
        tk.Button(self.root, text="Entrar", command=self.login).pack(pady=10)
        tk.Button(self.root, text="Registrar", command=self.register).pack()

    def setup_chat(self):
        self.clear_window()
        
        # Área de mensagens
        self.msg_area = scrolledtext.ScrolledText(self.root)
        self.msg_area.pack(expand=True, fill='both')
        self.msg_area.config(state='disabled')
        
        # Entrada de mensagem
        self.msg_entry = tk.Entry(self.root)
        self.msg_entry.pack(side='left', expand=True, fill='x')
        self.msg_entry.bind("<Return>", lambda e: self.send_msg())
        
        tk.Button(self.root, text="Enviar", command=self.send_msg).pack(side='right')
        
        # Atualizar mensagens a cada 2 segundos
        self.update_messages()
        self.root.after(2000, self.update_messages)

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def login(self):
        response = requests.post(f"{self.server_url}/login", json={
            "email": self.email_entry.get(),
            "password": self.password_entry.get()
        })
        if response.json().get("status") == "ok":
            self.user_id = response.json()["user_id"]
            self.setup_chat()
        else:
            messagebox.showerror("Erro", "Login falhou!")

    def register(self):
        email = self.email_entry.get()
        password = hashlib.sha256(self.password_entry.get().encode()).hexdigest()
        name = email.split("@")[0]
        
        conn = sqlite3.connect('chat.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (email, password, name) VALUES (?, ?, ?)", 
                     (email, password, name))
            conn.commit()
            messagebox.showinfo("Sucesso", "Registrado com sucesso!")
        except:
            messagebox.showerror("Erro", "Email já existe!")
        finally:
            conn.close()

    def send_msg(self):
        if not self.user_id or not self.msg_entry.get():
            return
        requests.post(f"{self.server_url}/send", json={
            "user_id": self.user_id,
            "text": self.msg_entry.get()
        })
        self.msg_entry.delete(0, 'end')
        self.update_messages()

    def update_messages(self):
        response = requests.get(f"{self.server_url}/messages")
        if response.status_code == 200:
            self.msg_area.config(state='normal')
            self.msg_area.delete(1.0, 'end')
            for msg in reversed(response.json()):
                self.msg_area.insert('end', f"{msg['name']} ({msg['time']}): {msg['text']}\n\n")
            self.msg_area.config(state='disabled')
        self.root.after(2000, self.update_messages)

if __name__ == "__main__":
    import sqlite3
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()
