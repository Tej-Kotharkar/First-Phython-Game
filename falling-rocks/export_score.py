import sqlite3, json

conn = sqlite3.connect("leaderboard.db")
cursor = conn.cursor()
cursor.execute("SELECT username, score FROM scores ORDER BY score DESC LIMIT 10")
data = [{"username": u, "score": s} for u, s in cursor.fetchall()]
conn.close()

with open("site/scores.json", "w") as f:
    json.dump(data, f, indent=2)

print("✅ Exported to site/scores.json")
