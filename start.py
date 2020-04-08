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
def api():
    products = get_json()
    return jsonify(products)


app.run(port=8080)