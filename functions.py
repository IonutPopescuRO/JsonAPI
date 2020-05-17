import json
import os
import pathlib
import re
import sqlite3
import random
import string

from flask import request
from flask_limiter.util import get_remote_address


def get_json(key, mode):
    data = []
    for path in pathlib.Path("db").rglob('*.json'):  # preluam recursiv fiecare fisier json din directorul /db
        if path.is_file() and (not str(path).startswith("db\\users") or (
                key is not None and mode and str(path).endswith(str(key) + ".json"))): # nu luam in considerare
            # directorul /db, decat in cazul in care mode este 1 sau 2
            if mode == 3 and not str(path).startswith("db\\users"): # daca modul selectat este 3, trecem mai departe
                # daca fisierul nu este cel al cheii
                continue
            with open(path) as json_file:
                try:
                    print(path)
                    new_data = json.load(json_file)
                    data.extend(new_data)
                except ValueError as e:  # daca gasim fisier cu format json invalid
                    print('invalid json: %s' % e)

    return data


def search_in_json(products, search, columns, limit2):
    result = []

    limit = len(products)  # numarul total al produselor
    if limit2 is not None:  # limitam rezultatele daca s-a cerut
        if limit2 < limit:
            limit = limit2

    for product in products:
        for key, value in product.items():
            if key in columns and search in str(value).lower():  # cautam doar in coloanele transmise
                result.append(product)
                if len(result) >= limit:
                    return result
                break

    return result


def sort_result(result, order_by, order, allowed_columns, errors):
    allowed_columns.append('ratings')  # initial coloana 'ratings' nu era specificata, deoarece contine doar numere,
    # si nu dorim cautarea acestora
    if order_by is not None and order_by in allowed_columns:
        desc = False

        if order is not None and order.lower() == "desc":
            desc = True
        result.sort(
            key=lambda product: sum(product[order_by]) / len(product[order_by]) if product[order_by] is not None else 0,
            reverse=desc)
    elif order_by is not None:  # afisam o eroare daca coloana ceruta nu exista
        errors.append({"error": 1, "description": "Unknown column: " + str(order_by)})

    return result


def result_limit(products, limit):  # limitarea rezultatelor
    result = []
    if limit == 0:
        return result

    if limit is None:
        result = products
    else:
        if limit > len(products):
            limit = len(products)
        result = products[:limit]
    return result


def parse_columns(columns, allowed_columns, errors):
    parsed_columns = allowed_columns  # daca nu s-a cerut nicio coloana specifica, le folosim pe toate
    not_found = []

    if columns is not None:
        if ',' in columns:
            parsed_columns = columns.split(',')
        else:
            parsed_columns = [columns]
    for x in parsed_columns:
        if x not in allowed_columns:
            not_found.append(x)

    if len(not_found):  # daca gasim o coloana ceruta de utilizator ce nu exista, afisam o eroare
        errors.append({"error": 1, "description": "Unknown columns: " + str(not_found)})
        parsed_columns = []
    return parsed_columns


def get_new_key():  # un string random de 32 de caractere continanda litere si cifre
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))


def get_rate_limit():  # transmitem limitele impuse api-ului, difera daca se ofera un key
    if request.remote_addr == '127.0.0.1':  # nu limitam daca sunt requesturi locale
        return None
    key = request.args.get('key', default=None, type=str)
    if check_key(None, key):
        return "500 per hour"
    return "50 per hour"


def get_key_func():  # transmitem pe ce criteriu se fac limitarile ( default: pe ip )
    if request.remote_addr == '127.0.0.1':  # nu limitam daca sunt requesturi locale
        return None
    key = request.args.get('key', default=None, type=str)
    if check_key(None, key):  # daca cheia exista, o folosim ca si criteriu de limitare
        return key
    return get_remote_address


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
    while check_key(conn,
                    key):  # in cazul in care cheia este deja folosita, generam altele pana cand dam de una nefolosita
        key = get_new_key()

    sql = 'INSERT INTO users(key, email) VALUES(?, ?)'
    cur = conn.cursor()
    cur.execute(sql, (key, email))
    conn.commit()

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
    if conn is None:
        conn = sqlite_connection()
    sql = 'SELECT id FROM users WHERE key = ? LIMIT 1'
    cur = conn.cursor()
    cur.execute(sql, (key,))

    row = cur.fetchone()
    if row is None:
        return False
    return True


def get_key_by_email(conn, email):
    sql = 'SELECT key FROM users WHERE email = ? LIMIT 1'
    cur = conn.cursor()
    cur.execute(sql, (email,))
    record = cur.fetchone()

    return record[0]


def get_email_by_key(conn, key):
    sql = 'SELECT email FROM users WHERE key = ? LIMIT 1'
    cur = conn.cursor()
    cur.execute(sql, (key,))
    record = cur.fetchone()

    return record[0]


def create_json_file(key):
    users = pathlib.Path("db/users")
    with open(os.path.join(users, key + '.json'), 'w') as outfile:
        json.dump([], outfile)


def check_url(link):  # django url validation regex
    # am extras functia din django, pentru a nu-l mai importa
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// sau https:// sau ftp
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domeniu
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...sau un ip
        r'(?::\d+)?'  # port optional
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return re.match(regex, link) is not None
