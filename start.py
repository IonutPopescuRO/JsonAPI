import flask
import requests
from flask import request, jsonify, render_template
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail, Message

from functions import *
from sqlite import *

app = flask.Flask(__name__)
app.config["DEBUG"] = True

app.config['MAIL_SERVER'] = 'mail.ionut.work'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = app.config['MAIL_DEFAULT_SENDER'] = 'json_api@ionut.work'
app.config['MAIL_PASSWORD'] = 'xiVkWNlWog'
mail = Mail(app)

limiter = Limiter(
    app,
    key_func=get_remote_address
)

allowed_columns = ['id', 'maker', 'img', 'url', 'title', 'description']
errors = []


@app.route('/', methods=['GET'])
def home():
    msg = Message("Subject", sender=('JsonAPI', app.config['MAIL_DEFAULT_SENDER']), recipients=['ionutpopescu10@yahoo.com'])
    #msg.body = "You have received a new feedback from {} <{}>.".format(name, email)
    msg.html = "<p>Mail body</p>"
    #mail.send(msg)
    status = {"name": "JsonAPI", "version": "v1.0", "status": 1}
    return render_template('index.html', status=str(status))


@app.route('/api/', methods=['GET'])
@limiter.limit("50 per hour")
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
    if columns is not None:
        columns.replace(" ", "")

    parsed_columns = parse_columns(columns, allowed_columns, api_errors)
    if search is not None:
        result = search_in_json(products, search, parsed_columns, limit)
    else:
        result = result_limit(products, limit)
    result = sort_result(result, order_by, order, allowed_columns, api_errors)

    if len(api_errors):
        return jsonify(api_errors)
    return jsonify(result)


@app.route('/api/admin/update/movies/<int:pages>/', methods=['GET'])
def external_api(pages=1):
    response = None
    new_json = []

    uri = "https://api.themoviedb.org/3/movie/top_rated?api_key=99e36b0bf3d6511077ee228f91e71dd5&language=ro&region=RO"
    try:
        response = requests.get(uri)
    except requests.ConnectionError:
        print("Connection Error")
    result = response.text
    movies = json.loads(result)['results']

    for movie in movies:
        new_movie = {"id": movie['id'], "maker": "themoviedb", "img": "https://image.tmdb.org/t/p/w600_and_h900_bestv2/"+str(movie['poster_path']), "url": "https://www.themoviedb.org/movie/"+str(movie['id']), "title": movie['title'], "description": movie['overview'], "ratings": [float(movie['vote_average'])/2]}
        new_json.append(new_movie)
    with open('db/movies.json', 'w') as outfile:
        json.dump(new_json, outfile, indent=4)

    return jsonify(movies)


@app.errorhandler(429)
def resource_not_found(e):
    return jsonify(error=str(e)), 429


app.run(port=8080)
