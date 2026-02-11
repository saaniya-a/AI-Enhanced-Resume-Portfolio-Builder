import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'resume_builder.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            version INTEGER NOT NULL,
            content TEXT NOT NULL,
            template TEXT DEFAULT 'classic',
            job_description TEXT,
            ats_score INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cover_letters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            resume_id INTEGER,
            content TEXT NOT NULL,
            job_description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (resume_id) REFERENCES resumes(id)
        )
    ''')

    conn.commit()
    conn.close()

def get_or_create_user(name):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE name = ?', (name,))
    user = cursor.fetchone()
    if not user:
        cursor.execute('INSERT INTO users (name) VALUES (?)', (name,))
        conn.commit()
        cursor.execute('SELECT * FROM users WHERE name = ?', (name,))
        user = cursor.fetchone()
    conn.close()
    return dict(user)

def save_resume(user_id, content, template='classic', job_description=None, ats_score=None):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT COALESCE(MAX(version), 0) FROM resumes WHERE user_id = ?', (user_id,))
    max_version = cursor.fetchone()[0]
    new_version = max_version + 1
    cursor.execute('''
        INSERT INTO resumes (user_id, version, content, template, job_description, ats_score)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, new_version, content, template, job_description, ats_score))
    conn.commit()
    resume_id = cursor.lastrowid
    conn.close()
    return resume_id, new_version

def get_user_resumes(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM resumes WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
    resumes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return resumes

def get_resume_by_id(resume_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM resumes WHERE id = ?', (resume_id,))
    resume = cursor.fetchone()
    conn.close()
    return dict(resume) if resume else None

def save_cover_letter(user_id, resume_id, content, job_description):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO cover_letters (user_id, resume_id, content, job_description)
        VALUES (?, ?, ?, ?)
    ''', (user_id, resume_id, content, job_description))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized.")
