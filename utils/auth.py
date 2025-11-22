import sqlite3       # For database connection
import bcrypt         # For password hashing
import jwt            # For token creation
import datetime       # For token expiry time

# Secret key for JWT encoding (keep this safe)
SECRET_KEY = "mysecretkey"

# Function to initialize database (creates users table)
def init_db():
    conn = sqlite3.connect("database/users.db")
    c = conn.cursor()

    # USERS TABLE
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE,
                    password TEXT,
                    name TEXT,
                    language TEXT,
                    age_group TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')

    # CONVERSATIONS TABLE
    c.execute('''CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )''')

    # MESSAGES TABLE
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER,
                    sender VARCHAR(10),
                    message_content TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    feedback TEXT,
                    FOREIGN KEY(conversation_id) REFERENCES conversations(id)
                )''')

    # FEEDBACK TABLE
    c.execute('''CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    query TEXT,
                    bot_response TEXT,
                    rating TEXT,
                    comment TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )''')

    conn.commit()
    conn.close()


# Function to register a new user
def register_user(email, password, name, language, age_group):
    conn = sqlite3.connect("database/users.db")
    c = conn.cursor()
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        c.execute("INSERT INTO users (email, password, name, language, age_group) VALUES (?, ?, ?, ?, ?)",
                  (email, hashed, name, language, age_group))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# Function to verify user login credentials
def login_user(email, password):
    conn = sqlite3.connect("database/users.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    conn.close()
    if user and bcrypt.checkpw(password.encode('utf-8'), user[2]):
        # Create a JWT token if credentials match
        token = jwt.encode({
            "email": email,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, SECRET_KEY, algorithm="HS256")
        return token
    return None
def get_user_id(email):
    conn = sqlite3.connect("database/users.db")
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE email = ?", (email,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None
def get_user_language(email):
    conn = sqlite3.connect("database/users.db")
    c = conn.cursor()
    c.execute("SELECT language FROM users WHERE email = ?", (email,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else "English"
