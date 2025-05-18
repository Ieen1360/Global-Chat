from flask import Flask, request, jsonify
from datetime import datetime
import sqlite3, hashlib

app = Flask(__name__)

# Banco de dados simplificado
def init_db():
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, email TEXT, password TEXT, name TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY, user_id INTEGER, text TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

@app.route('/send', methods=['POST'])
def send_message():
    data = request.json
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute("INSERT INTO messages (user_id, text, timestamp) VALUES (?, ?, ?)",
              (data['user_id'], data['text'], datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})

@app.route('/messages', methods=['GET'])
def get_messages():
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('''SELECT messages.id, users.name, messages.text, messages.timestamp 
                 FROM messages JOIN users ON messages.user_id = users.id
                 ORDER BY messages.timestamp DESC LIMIT 50''')
    messages = [{"id": row[0], "name": row[1], "text": row[2], "time": row[3]} for row in c.fetchall()]
    conn.close()
    return jsonify(messages)

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute("SELECT id, name FROM users WHERE email=? AND password=?", 
              (data['email'], hashlib.sha256(data['password'].encode()).hexdigest()))
    user = c.fetchone()
    conn.close()
    if user:
        return jsonify({"status": "ok", "user_id": user[0], "name": user[1]})
    return jsonify({"status": "error"}), 401

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
