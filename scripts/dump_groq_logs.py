import sqlite3, json
from pathlib import Path
p=Path('app/data/app.db')
conn=sqlite3.connect(str(p))
conn.row_factory=sqlite3.Row
cur=conn.cursor()
cur.execute("SELECT * FROM groq_logs ORDER BY id DESC LIMIT 20")
rows=cur.fetchall()
for r in rows:
    print(json.dumps(dict(r), ensure_ascii=False))
conn.close()