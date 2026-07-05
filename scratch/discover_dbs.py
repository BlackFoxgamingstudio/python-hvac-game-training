import sqlite3
import os

dbs = [
    "/Users/russellpowers/Sovereign Biz Box/databases/sbb_command_center.db",
    "/Users/russellpowers/Sovereign Biz Box/llm dev/sbb_learning_and_growth.db"
]

for db in dbs:
    if os.path.exists(db):
        print(f"\n=================== Database: {db} ===================")
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for t in tables:
            table_name = t[0]
            print(f"Table: {table_name}")
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
        conn.close()
    else:
        print(f"Database not found: {db}")
