import sqlite3

def create_advanced_schema(db_path=None):
    if db_path is None:
        import os
        from config import BACKEND_DIR
        db_path = os.path.join(BACKEND_DIR, "db", "users.db")
        
        # Ensure the db directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # User Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # Conversations Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                sub_question TEXT,
                response TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
            """)

            # Chat History Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                role TEXT CHECK(role IN ('user', 'assistant')) NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
            """)

            print("✅ Database schema created successfully.")
    except Exception as e:
        print("❌ Failed to create schema:", e)

if __name__ == "__main__":
    create_advanced_schema()


