"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

#PEOPLE
@app.route('/people')
def get_all_people():
    all_people = People.query.all()
    return jsonify(list(map(lambda item: item.serialize(), all_people))), 200

@app.route('/people/<int:people_id>', methods = ['GET'])
def get_people_id(people_id = None):

    person = People.query.filter_by(id = people_id).one_or_none()
    if person is None:
        return jsonify({"message" : "No coincidence"}), 400

    return jsonify(person.serialize()), 200

@app.route('/people', methods = ['POST'])
def add_people():
    data = request.json
    
    if data is None or data is {}:
        return jsonify({"message" : "data is empty"}), 400

    people = People()
    people.name = data.get('name', None)
    people.gender = data.get('gender', None)
    people.skin_color = data.get('skin_color', None)
    people.birth_year = data.get('birth_year', None)

    db.session.add(people)

    try:
        db.session.commit()
    except Exception as err:
        db.session.rollback()
        return jsonify({'message': err.args}), 500    

    return jsonify({"message" : "People correctly added"}), 200    

# PLANET
@app.route('/planet')
def get_all_planet():
    all_planets = Planet.query.all()
    return jsonify(list(map(lambda item: item.serialize(), all_planets))), 200

@app.route('/planet/<int:planet_id>', methods = ['GET'])
def get_planet(planet_id = None):

    planet = Planet.query.filter_by(id = planet_id).one_or_none()
    if planet is None:
        return jsonify({"message" : "No coincidence"}), 400

    return jsonify(planet.serialize()), 200

@app.route('/planet', methods = ['POST'])
def add_planet():
    data = request.json
    
    if data is None or data is {}:
        return jsonify({"message" : "data is empty"}), 400

    planet = Planet()
    planet.name = data.get('name', None)
    planet.climate = data.get('climate', None)
    planet.terrain = data.get('terrain', None)
    planet.population = data.get('population', None)

    db.session.add(planet)

    try:
        db.session.commit()
    except Exception as err:
        db.session.rollback()
        return jsonify({'message': err.args}), 500    

    return jsonify({"message" : "Planet correctly added"}), 200    

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
