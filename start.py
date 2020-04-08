import flask
from flask import jsonify, render_template
import json

app = flask.Flask(__name__)
app.config["DEBUG"] = True


def get_json():
    data = None
    with open('db/products.json') as json_file:
        data = json.load(json_file)
    return data


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/api/', methods=['GET'])
@app.route('/api/<int:limit>/', methods=['GET'])
@app.route('/api/<int:limit>/<string:order_by>/<string:order>/', methods=['GET'])
@app.route('/api/<string:action>/<int:limit>/', methods=['GET'])
@app.route('/api/<string:action>/<string:columns>', methods=['GET'])
@app.route('/api/<string:action>/<string:columns>/<string:search>/', methods=['GET'])
@app.route('/api/<string:action>/<string:columns>/<string:search>/<string:order_by>/<string:order>/', methods=['GET'])
@app.route('/api/<string:action>/<string:columns>/<string:search>/<int:limit>/', methods=['GET'])
@app.route('/api/<string:action>/<string:columns>/<string:search>/<int:limit>/<string:order_by>/<string:order>/', methods=['GET'])
def api(action=None, columns=None, search=None, limit=None, order_by=None, order=None):
    products = get_json()
    result = []

    #if action is None:
    #    result = products
    return jsonify(result)


app.run(port=8080)