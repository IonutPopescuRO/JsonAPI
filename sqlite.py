import os
import pathlib
import sqlite3
from functions import get_new_key


def sqlite_connection():
    conn = None
    db = pathlib.Path("db")
    try:
        conn = sqlite3.connect(os.path.join(db, 'users.db'))
    except sqlite3.Error as e:
        print(e)

    return conn


def insert_user(conn, email):
    key = get_new_key()
    while check_key(conn, key):
        key = get_new_key()

    sql = 'INSERT INTO users(key, email) VALUES(?, ?)'
    cur = conn.cursor()
    cur.execute(sql, (key, email))

    return key


def delete_task(conn, email):
    sql = 'DELETE FROM users WHERE email = ?'
    cur = conn.cursor()
    cur.execute(sql, (email,))
    conn.commit()


def check_email(conn, email):
    sql = 'SELECT id FROM users WHERE email = ? LIMIT 1'
    cur = conn.cursor()
    cur.execute(sql, (email,))

    row = cur.fetchone()
    if row is None:
        return True
    return False


def check_key(conn, key):
    sql = 'SELECT id FROM users WHERE key = ? LIMIT 1'
    cur = conn.cursor()
    cur.execute(sql, (key,))

    row = cur.fetchone()
    if row is None:
        return False
    return True
