import sqlite3


def build_query(username):
    return "SELECT * FROM users WHERE username = '" + username + "'"


def find_user(username):
    conn = sqlite3.connect(":memory:")
    rows = conn.execute(build_query(username)).fetchall()
    conn.close()
    return rows
