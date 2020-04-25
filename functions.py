import json
import pathlib
import random
import string

from flask import request
from flask_limiter.util import get_remote_address


def get_json():
    data = []
    for path in pathlib.Path("db").rglob('*.json'): # preluam recursiv fiecare fisier json din directorul /db
        if path.is_file():
            with open(path) as json_file:
                try:
                    new_data = json.load(json_file)
                    data.extend(new_data)
                except ValueError as e: # daca gasim fisier cu format json invalid
                    print('invalid json: %s' % e)

    return data


def search_in_json(products, search, columns, limit2):
    result = []

    limit = len(products) # numarul total al produselor
    if limit2 is not None: # limitam rezultatele daca s-a cerut
        if limit2 < limit:
            limit = limit2

    for product in products:
        for key, value in product.items():
            if key in columns and search in str(value).lower(): # cautam doar in coloanele transmise
                result.append(product)
                if len(result) >= limit:
                    return result
                break

    return result


def sort_result(result, order_by, order, allowed_columns, errors):
    allowed_columns.append('ratings') # initial coloana 'ratings' nu era specificata, deoarece contine doar numere,
    # si nu dorim cautarea acestora
    if order_by is not None and order_by in allowed_columns:
        desc = False

        if order is not None and order.lower() == "desc":
            desc = True
        result.sort(key=lambda product: sum(product[order_by]) / len(product[order_by]) if product[order_by] is not None else 0, reverse=desc)
    elif order_by is not None: # afisam o eroare daca coloana ceruta nu exista
        errors.append({"error": 1, "description": "Unknown column: " + str(order_by)})

    return result


def result_limit(products, limit): # limitarea rezultatelor
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
    parsed_columns = allowed_columns # daca nu s-a cerut nicio coloana specifica, le folosim pe toate
    not_found = []

    if columns is not None:
        if ',' in columns:
            parsed_columns = columns.split(',')
        else:
            parsed_columns = [columns]
    for x in parsed_columns:
        if x not in allowed_columns:
            not_found.append(x)

    if len(not_found): # daca gasim o coloana ceruta de utilizator ce nu exista, afisam o eroare
        errors.append({"error": 1, "description": "Unknown columns: "+str(not_found)})
        parsed_columns = []
    return parsed_columns


def get_new_key(): # un string random de 32 de caractere continanda litere si cifre
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))


def get_rate_limit(): # transmitem limitele impuse api-ului, difera daca se ofera un key
    key = request.args.get('key', default=None, type=str)
    if key == '123':
        return "6 per minute"
    #return "50 per hour"
    return "4 per minute"


def get_key_func(): # transmitem pe ce criteriu se fac limitarile ( default: pe ip )
    if request.remote_addr == '127.0.0.1':  # nu limitam daca sunt requesturi locale
        return None
    key = request.args.get('key', default=None, type=str)
    if key == '123':
        return '123'
    return get_remote_address

