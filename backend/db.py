# db.py
import os, sqlite3
from hashlib import sha256
from typing import Optional, List, Tuple

DB_PATH = 'users.db'

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_connection() as conn:
        # Remove tabela antiga
        conn.execute("DROP TABLE IF EXISTS users;")
        # Cria a tabela NOVA, com DEFAULT CURRENT_TIMESTAMP
        conn.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT         NOT NULL,
            email TEXT        UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.commit()
        
def create_user(name: str, email: str, password: str) -> int:
    pwd_hash = sha256(password.encode()).hexdigest()
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, pwd_hash)
        )
        conn.commit()
        return cursor.lastrowid

def get_user_by_email(email: str) -> Optional[Tuple]:
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT id, name, email, created_at FROM users WHERE email = ?",
            (email,)
        )
        return cursor.fetchone()

def list_users() -> List[Tuple]:
    with get_connection() as conn:
        cursor = conn.execute("SELECT id, name, email, created_at FROM users")
        return cursor.fetchall()

def get_user_record(email: str) -> Optional[Tuple]:
    """
    Retorna tupla completa (id, name, email, password_hash, created_at)
    ou None se não existir.
    """
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT id, name, email, password_hash, created_at FROM users WHERE email = ?",
            (email,)
        )
        return cursor.fetchone()

def authenticate_user(email: str, password: str) -> Optional[Tuple]:
    """
    Verifica se email e senha coincidem. Se OK, retorna (id, name, email, created_at);
    se falhar (usuário não existe ou senha incorreta), retorna None.
    """
    record = get_user_record(email)
    if not record:
        return None

    stored_hash = record[3]  # password_hash
    incoming_hash = sha256(password.encode()).hexdigest()
    if incoming_hash == stored_hash:
        # retorna sem o hash: (id, name, email, created_at)
        return (record[0], record[1], record[2], record[4])
    return None