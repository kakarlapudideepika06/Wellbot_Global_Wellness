import sqlite3
from datetime import datetime

DB_PATH = "database/users.db"

def start_conversation(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO conversations (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conv_id = c.lastrowid
    conn.close()
    return conv_id

def log_message(conversation_id, sender, text, feedback=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO messages (conversation_id, sender, message_content, feedback) VALUES (?, ?, ?, ?)",
        (conversation_id, sender, text, feedback)
    )
    conn.commit()
    conn.close()

def store_feedback(user_id, query, bot_response, rating, comment=""):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO feedback (user_id, query, bot_response, rating, comment) VALUES (?, ?, ?, ?, ?)",
        (user_id, query, bot_response, rating, comment)
    )
    conn.commit()
    conn.close()
