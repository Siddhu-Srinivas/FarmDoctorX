import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'db', 'history.db')

def init_db():
    """Initialize the SQLite database with conversation history table."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            solution_type TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def save_conversation(question, answer, solution_type):
    """Save a conversation to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    timestamp = datetime.now().isoformat()
    
    cursor.execute(
        'INSERT INTO conversation_history (question, answer, solution_type, timestamp) VALUES (?, ?, ?, ?)',
        (question, answer, solution_type, timestamp)
    )
    
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    
    return last_id

def get_all_conversations():
    """Get all conversations from the database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM conversation_history ORDER BY id DESC')
    conversations = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return conversations

def get_conversation_by_id(conversation_id):
    """Get a specific conversation by ID."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM conversation_history WHERE id = ?', (conversation_id,))
    conversation = cursor.fetchone()
    
    conn.close()
    return dict(conversation) if conversation else None

def delete_conversation(conversation_id):
    """Delete a specific conversation."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM conversation_history WHERE id = ?', (conversation_id,))
    
    conn.commit()
    conn.close()

def clear_all_conversations():
    """Delete all conversations."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM conversation_history')
    
    conn.commit()
    conn.close()

def get_conversations_paginated(page=1, per_page=20):
    """Get conversations with pagination."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    offset = (page - 1) * per_page
    
    cursor.execute('SELECT COUNT(*) as total FROM conversation_history')
    total = cursor.fetchone()['total']
    
    cursor.execute(
        'SELECT * FROM conversation_history ORDER BY id DESC LIMIT ? OFFSET ?',
        (per_page, offset)
    )
    conversations = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        'conversations': conversations,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page
    }

def search_conversations(query):
    """Search conversations by question text."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    search_term = f"%{query}%"
    cursor.execute(
        'SELECT * FROM conversation_history WHERE question LIKE ? ORDER BY id DESC',
        (search_term,)
    )
    conversations = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return conversations

def filter_by_solution_type(solution_type):
    """Filter conversations by solution type."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT * FROM conversation_history WHERE solution_type = ? ORDER BY id DESC',
        (solution_type,)
    )
    conversations = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return conversations

# Initialize database on import
init_db()
