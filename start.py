import flask
from flask import jsonify, render_template
from functions import *

app = flask.Flask(__name__)
app.config["DEBUG"] = True

allowed_columns = ['id', 'maker', 'img', 'url', 'title', 'description']
errors = []


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
    errors = []
    products = get_json()
    result = result_limit(products, limit)
    result = sort_result(result, order_by, order, allowed_columns, errors)

    if len(errors):
        return jsonify(errors)
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
    result = errors = []
    if limit == 0:
        return jsonify(result)
    products = get_json()

    parsed_columns = parse_columns(columns, allowed_columns, errors)
    result = search_in_json(products, search, parsed_columns, limit)
    result = sort_result(result, order_by, order, allowed_columns, errors)

    if len(errors):
        return jsonify(errors)
    return jsonify(result)


app.run(port=8080)
