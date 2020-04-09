import flask
from flask import request, jsonify, render_template
from functions import *

app = flask.Flask(__name__)
app.config["DEBUG"] = True

allowed_columns = ['id', 'maker', 'img', 'url', 'title', 'description']
errors = []


@app.route('/', methods=['GET'])
def home():
    status = {"name": "JsonAPI", "version": "v1.0", "status": 1}
    return render_template('index.html', status=str(status))


@app.route('/api/', methods=['GET'])
def api():
    search = request.args.get('search', default=None, type=str)
    columns = request.args.get('columns', default=None, type=str)
    limit = request.args.get('limit', default=None, type=int)
    order_by = request.args.get('order_by', default=None, type=str)
    order = request.args.get('order', default=None, type=str)

    result = api_errors = []
    if limit == 0:
        return jsonify(result)

    products = get_json()

    parsed_columns = parse_columns(columns, allowed_columns, api_errors)
    if search is not None:
        result = search_in_json(products, search, parsed_columns, limit)
    else:
        result = result_limit(products, limit)
    result = sort_result(result, order_by, order, allowed_columns, api_errors)

    if len(api_errors):
        return jsonify(api_errors)
    return jsonify(result)


app.run(port=8080)
