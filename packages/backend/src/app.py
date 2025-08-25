from flask import Flask, request, jsonify
from main import ask_idc_chatbot
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

def init_db():
    """Initialize database with required tables"""
    import os
    from config import BACKEND_DIR
    db_path = os.path.join(BACKEND_DIR, "db", "users.db")
    
    # Ensure the db directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("Database initialized successfully")

def get_db():
    import os
    from config import BACKEND_DIR
    db_path = os.path.join(BACKEND_DIR, "db", "users.db")
    
    # Ensure the db directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def home():
    return "IDC Chatbot API is running."

@app.route("/register", methods=["POST"])
def register_user():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return jsonify({"error": "Name and email are required."}), 400

    conn = get_db()
    try:
        conn.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already registered."}), 409
    finally:
        conn.close()

    return jsonify({"message": "User registered successfully."})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    
    # Handle both old and new request formats for backward compatibility
    email = data.get("email") or data.get("user", {}).get("email")
    query = data.get("query") or data.get("message")

    if not email or not query:
        return jsonify({"error": "Email and message are required."}), 400

    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()

    if not user:
        return jsonify({"error": "Email not registered."}), 403

    response = ask_idc_chatbot(query)
    return jsonify({"response": response})

# Initialize database on startup
init_db()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
