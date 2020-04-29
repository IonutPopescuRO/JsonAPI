"""
Resurse:
https://programminghistorian.org/en/lessons/creating-apis-with-python-and-flask
https://flask-limiter.readthedocs.io/en/stable/
https://pythonhosted.org/Flask-Mail/
https://dev.to/mikecase/flask-wtf-recaptcha-not-working-26ml
"""
import time

import flask
import requests
from flask import jsonify, render_template, Response
from flask_limiter import Limiter
from flask_mail import Mail, Message

from config import RegisterForm
from functions import *

app = flask.Flask(__name__)
app.config.from_object("config.Config")  # Folosim o clasa pentru configurarea Flask

mail = Mail(app)
limiter = Limiter(app, key_func=get_remote_address)

allowed_columns = ['id', 'maker', 'img', 'url', 'title',
                   'description']  # coloanele care vor fi permise pentru cautare si sortare
errors = []


@app.route('/', methods=['GET'])
def home():
    msg = Message("Subject", sender=('JsonAPI', app.config['MAIL_DEFAULT_SENDER']),
                  recipients=['ionutpopescu10@yahoo.com'])
    # msg.body = "You have received a new feedback from {} <{}>.".format(name, email)
    msg.html = "<p>Mail body</p>"
    # mail.send(msg)
    status = {"name": "JsonAPI", "version": "v1.0", "status": 1}  # un status demo
    return render_template('index.html', status=str(status))


@app.route('/api/', methods=['GET'])
@limiter.limit(get_rate_limit, key_func=get_key_func)
def api():
    search = request.args.get('search', default=None, type=str)
    columns = request.args.get('columns', default=None, type=str)
    limit = request.args.get('limit', default=None, type=int)
    order_by = request.args.get('order_by', default=None, type=str)
    order = request.args.get('order', default=None, type=str)
    download = request.args.get('download', default=0, type=int)

    result = api_errors = []
    if limit == 0:  # daca limita impusa este 0, nu mai are rost sa continuam
        return jsonify(result)

    products = get_json()
    if columns is not None:
        columns.replace(" ", "")

    parsed_columns = parse_columns(columns, allowed_columns, api_errors)  # impunem coloanele in care se cauta
    if search is not None:
        result = search_in_json(products, search, parsed_columns, limit)
    else:
        result = result_limit(products, limit)  # daca nu se cauta dupa ceva anume, doar limitam rezultatele
    result = sort_result(result, order_by, order, allowed_columns, api_errors)

    if len(api_errors):  # daca am avut erori pe parcrusul executiei, le returnam
        return jsonify(api_errors)

    if download > 0:  # daca se doreste descarcarea rezultatului
        return Response(
            jsonify(result).get_data(as_text=True),
            mimetype="application/json",
            headers={"Content-disposition": "attachment; filename="+ str(int(time.time()) )+".json"})

    return jsonify(result)


@app.route('/api/admin/update/movies/<int:pages>/', methods=['GET'])  # ruta adaugata pentru a imbogati json-ul
def external_api(pages=1):
    response = None
    new_json = []
    # am ales al intamplare un api ce ofera recomandari de filme
    uri = "https://api.themoviedb.org/3/movie/top_rated?api_key=99e36b0bf3d6511077ee228f91e71dd5&language=ro&region=RO"
    try:
        response = requests.get(uri)
    except requests.ConnectionError:
        print("Connection Error")
    result = response.text
    movies = json.loads(result)['results']

    for movie in movies:
        new_movie = {"id": movie['id'], "maker": "themoviedb",
                     "img": "https://image.tmdb.org/t/p/w600_and_h900_bestv2/" + str(movie['poster_path']),
                     "url": "https://www.themoviedb.org/movie/" + str(movie['id']), "title": movie['title'],
                     "description": movie['overview'],
                     "ratings": [float(movie['vote_average']) / 2]}  # formatam totul folosind coloanele noastre
        new_json.append(new_movie)
    with open('db/movies.json', 'w') as outfile:
        json.dump(new_json, outfile, indent=4)

    return jsonify(movies)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        return render_template("register.html", form=form, message='test', alert='success')

    return render_template("register.html", form=form)


@app.errorhandler(429)  # afisam eroarea produsa de rate limiting in format json
def resource_not_found(e):
    return jsonify(error=str(e)), 429


app.run(port=8080)
