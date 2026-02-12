import sqlite3, os

DB_PATH = os.path.join(os.path.dirname(__file__), 'resume_builder.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    db.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, email TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(name, email));
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL, version INTEGER NOT NULL,
            label TEXT DEFAULT '', content TEXT NOT NULL,
            template TEXT DEFAULT 'classic', job_description TEXT,
            ats_score INTEGER, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id));
    ''')
    try: db.execute('ALTER TABLE resumes ADD COLUMN label TEXT DEFAULT ""')
    except: pass
    try: db.execute('ALTER TABLE users ADD COLUMN email TEXT DEFAULT ""')
    except: pass
    db.commit()
    db.close()

def get_or_create_user(name, email):
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE name = ? AND email = ?', (name, email)).fetchone()
    if not user:
        db.execute('INSERT INTO users (name, email) VALUES (?, ?)', (name, email))
        db.commit()
        user = db.execute('SELECT * FROM users WHERE name = ? AND email = ?', (name, email)).fetchone()
    db.close()
    return dict(user)

def save_resume(user_id, content, template='classic', job_description=None, ats_score=None, label=''):
    db = get_db()
    ver = db.execute('SELECT COALESCE(MAX(version),0) FROM resumes WHERE user_id=?', (user_id,)).fetchone()[0] + 1
    db.execute('INSERT INTO resumes (user_id,version,label,content,template,job_description,ats_score) VALUES (?,?,?,?,?,?,?)',
               (user_id, ver, label, content, template, job_description, ats_score))
    db.commit()
    rid = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    db.close()
    return rid, ver

def get_user_resumes(user_id):
    db = get_db()
    rows = [dict(r) for r in db.execute('SELECT * FROM resumes WHERE user_id=? ORDER BY created_at DESC', (user_id,)).fetchall()]
    db.close()
    return rows

def get_resume_by_id(rid):
    db = get_db()
    r = db.execute('SELECT * FROM resumes WHERE id=?', (rid,)).fetchone()
    db.close()
    return dict(r) if r else None

def delete_resume(rid, uid):
    db = get_db()
    db.execute('DELETE FROM resumes WHERE id=? AND user_id=?', (rid, uid))
    db.commit()
    db.close()

def rename_resume(rid, uid, label):
    db = get_db()
    db.execute('UPDATE resumes SET label=? WHERE id=? AND user_id=?', (label, rid, uid))
    db.commit()
    db.close()