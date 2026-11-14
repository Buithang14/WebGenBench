import sqlite3

conn = sqlite3.connect('storage/webgenbench.db')
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in cur.fetchall()]
print("Danh sách bảng trong SQLite database:")
for t in tables:
    cur.execute(f"SELECT COUNT(*) FROM [{t}];")
    cnt = cur.fetchone()[0]
    print(f" - Bảng '{t}': {cnt} dòng dữ liệu")
conn.close()
