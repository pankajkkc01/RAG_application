import sqlite3
from datetime import datetime
import os

DB_NAME = os.path.join(os.path.dirname(__file__), "rag_app.db")


#DB_NAME = "rag_app.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# ----------------- CHAT LOGS ----------------- #

def create_application_logs():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS application_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            user_query TEXT,
            gpt_response TEXT,
            model TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.close()

def insert_application_logs(session_id, user_query, gpt_response, model):
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO application_logs (session_id, user_query, gpt_response, model)
        VALUES (?, ?, ?, ?)
    ''', (session_id, user_query, gpt_response, model))
    conn.commit()
    conn.close()

def get_chat_history(session_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT user_query, gpt_response
        FROM application_logs
        WHERE session_id = ?
        ORDER BY created_at
    ''', (session_id,))
    messages = []
    for row in cursor.fetchall():
        messages.extend([
            {"role": "human", "content": row["user_query"]},
            {"role": "ai", "content": row["gpt_response"]}
        ])
    conn.close()
    return messages

# ----------------- DOCUMENTS ----------------- #

def create_document_store():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS document_store (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.close()

def insert_document_record(filename):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO document_store (filename) VALUES (?)', (filename,))
    file_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return file_id

def delete_document_record(file_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM document_store WHERE id = ?', (file_id,))
    conn.commit()
    conn.close()
    return True

def get_all_documents():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, filename, upload_timestamp
        FROM document_store
        ORDER BY upload_timestamp DESC
    ''')
    documents = cursor.fetchall()
    conn.close()
    return [dict(doc) for doc in documents]

# ----------------- FEEDBACK ----------------- #

def create_feedback_logs():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS feedback_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            user_query TEXT,
            model_response TEXT,
            feedback TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.close()

def insert_feedback_log(session_id, user_query, model_response, feedback):
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO feedback_logs (session_id, user_query, model_response, feedback)
        VALUES (?, ?, ?, ?)
    ''', (session_id, user_query, model_response, feedback))
    conn.commit()
    conn.close()

# ----------------- USER LOGIN ----------------- #

def create_user_login_table():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS user_logins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.close()

def insert_user_login(name, email, phone):
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO user_logins (name, email, phone)
        VALUES (?, ?, ?)
    ''', (name, email, phone))
    conn.commit()
    conn.close()

def get_all_logged_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, name, email, phone, login_time
        FROM user_logins
        ORDER BY login_time DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": row["id"],
            "name": row["name"],
            "email": row["email"],
            "phone": row["phone"],
            "login_time": row["login_time"]
        }
        for row in rows
    ]

# ----------------- Create allowed user table ----------------- #
def create_allowed_users_table():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS allowed_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT
        )
    ''')
    conn.close()

def insert_allowed_users(users):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.executemany(
        '''
        INSERT INTO allowed_users (name, email, phone)
        VALUES (?, ?, ?)
        ''',
        [(u["name"], u["email"], u["phone"]) for u in users]
    )
    conn.commit()
    conn.close()

def delete_allowed_user(email):
    conn = get_db_connection()
    conn.execute('DELETE FROM allowed_users WHERE email = ?', (email,))
    conn.commit()
    conn.close()

def is_user_allowed(name, email, phone):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT COUNT(*) FROM allowed_users
        WHERE LOWER(TRIM(name)) = LOWER(TRIM(?))
          AND LOWER(TRIM(email)) = LOWER(TRIM(?))
          AND TRIM(phone) = TRIM(?)
        ''',
        (name, email, phone)
    )
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

def list_allowed_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT name, email, phone FROM allowed_users')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]




# ----------------- INIT ALL TABLES ----------------- #

create_application_logs()
create_document_store()
create_feedback_logs()
create_user_login_table()
create_allowed_users_table()
