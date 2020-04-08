import json


def get_json():
    data = None
    with open('db/products.json') as json_file:
        data = json.load(json_file)
    return data


def search_in_json(products, search, columns, limit2):
    result = []

    limit = len(products)
    if limit2 is not None:
        if limit2 < limit:
            limit = limit2

    for product in products:
        for key, value in product.items():
            if key in columns and search in str(value).lower():
                result.append(product)
                if len(result) >= limit:
                    return result
                break

    return result


def sort_result(result, order_by, order, allowed_columns, errors):
    allowed_columns.append('ratings')
    if order_by is not None and order_by in allowed_columns:
        if order_by == "ratings":
            result.sort(
                key=lambda product: (sum((product[order_by] is not None, 0)) / len((product[order_by] is not None, 0))))
        else:
            result.sort(key=lambda product: product[order_by])

        if order is not None and order.lower() == "desc":
            result.reverse()
    elif order_by is not None:
        errors.append({"error": 1, "description": "Unknown column: " + str(order_by)})
    return result


def result_limit(products, limit):
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
    parsed_columns = allowed_columns
    not_found = []

    if columns is not None:
        if ',' in columns:
            parsed_columns = columns.split(',')
        else:
            parsed_columns = [columns]
    for x in parsed_columns:
        if x not in allowed_columns:
            not_found.append(x)

    if len(not_found):
        errors.append({"error": 1, "description": "Unknown columns: "+str(not_found)})
        parsed_columns = []
    return parsed_columns
