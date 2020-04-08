import flask
from flask import jsonify, render_template
import json

app = flask.Flask(__name__)
app.config["DEBUG"] = True

allowed_columns = ['id', 'maker', 'img', 'url', 'title', 'description']


def get_json():
    data = None
    with open('db/products.json') as json_file:
        data = json.load(json_file)
    return data


def search_in_json(products, search=None, columns=None, limit2=None):
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


def sort_result(result, order_by=None, order=None):
    if order_by is not None and order_by in allowed_columns:
        rev = False

        if order_by == "ratings":
            result.sort(key=lambda product: (sum((product[order_by] is not None, 0))/len((product[order_by] is not None, 0))))
        else:
            result.sort(key=lambda product: product[order_by])

        if order is not None and order.lower() == "desc":
            result.reverse()

    return result


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/api/', methods=['GET'])
@app.route('/api/<int:limit>/', methods=['GET'])
@app.route('/api/<int:limit>/<string:order_by>/', methods=['GET'])
@app.route('/api/<int:limit>/<string:order_by>/<string:order>/', methods=['GET'])
@app.route('/api/<string:order_by>/', methods=['GET'])
@app.route('/api/<string:order_by>/<string:order>/', methods=['GET'])
def simple_api(action=None, limit=None, order_by=None, order=None):
    products = get_json()
    result = []

    if limit is None:
        result = products
    else:
        if limit > len(products):
            limit = len(products)
        result = products[:limit]

    allowed_columns.append('ratings')
    if order_by is not None and order_by in allowed_columns:
        result = sort_result(result, order_by, order)

    return jsonify(result)


@app.route('/api/search/<string:search>/', methods=['GET'])
@app.route('/api/search/<string:search>/<string:columns>/', methods=['GET'])
@app.route('/api/search/<string:search>/<string:columns>/<string:order_by>/', methods=['GET'])
@app.route('/api/search/<string:search>/<string:columns>/<string:order_by>/<string:order>/', methods=['GET'])
@app.route('/api/search/<string:search>/<string:columns>/<int:limit>/', methods=['GET'])
@app.route('/api/search/<string:search>/<string:columns>/<int:limit>/<string:order_by>/<string:order>/',
           methods=['GET'])
@app.route('/api/search/<string:search>/<string:columns>/<int:limit>/<string:order_by>/', methods=['GET'])
def api(columns=None, search=None, limit=None, order_by=None, order=None):
    result = []
    if limit == 0:
        return jsonify(result)
    products = get_json()
    parsed_columns = allowed_columns

    if columns is not None:
        if ',' in columns:
            parsed_columns = str.split(',')
        else:
            parsed_columns = [columns]

    result = search_in_json(products, search, parsed_columns, limit)

    allowed_columns.append('ratings')
    if order_by is not None and order_by in allowed_columns:
        result = sort_result(result, order_by, order)

    return jsonify(result)


app.run(port=8080)
