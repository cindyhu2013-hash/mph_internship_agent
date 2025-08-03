import hashlib, sqlite3, os

DB_PATH = '.state/db.sqlite3'
os.makedirs('.state', exist_ok=True)
conn = sqlite3.connect(DB_PATH)
conn.execute('create table if not exists hashes (h text primary key)')
conn.commit()

def seen_before(h):
    cur = conn.execute('select 1 from hashes where h=?', (h,))
    return cur.fetchone() is not None

def remember(h):
    conn.execute('insert or ignore into hashes (h) values (?)',(h,))
    conn.commit()

def hash_job(j):
    base = f"{j['title'].lower()}|{j['organization'].lower()}|{j.get('location','').lower()}"
    return hashlib.sha256(base.encode()).hexdigest()[:16]
