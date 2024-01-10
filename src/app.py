import os
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, Favorite

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

# People Endpoints
@app.route('/people', methods=['GET'])
def get_people():
    characters = Character.query.all()
    character_list = [{'id': character.id, 'name': character.name} for character in characters]
    return jsonify(character_list)

@app.route('/people/<int:people_id>', methods=['GET'])
def get_people_id(people_id):
    character = Character.query.get(people_id)
    if character:
        return jsonify({'id': character.id, 'name': character.name})
    else:
        return jsonify({'error': 'Character not found'}), 404

# Planets Endpoints
@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    planet_list = [{'id': planet.id, 'name': planet.name} for planet in planets]
    return jsonify(planet_list)

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planets_id(planet_id):
    planet = Planet.query.get(planet_id)
    if planet:
        return jsonify({'id': planet.id, 'name': planet.name})
    else:
        return jsonify({'error': 'Planet not found'}), 404

# Users Endpoints
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    user_list = [{'id': user.id, 'email': user.email} for user in users]
    return jsonify(user_list)

# Favorites Endpoints
@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    current_user_id = 1  # Simulated current user ID (replace with actual authentication)
    user_favorites = Favorite.query.filter_by(user_id=current_user_id).all()

    favorites_list = []
    for favorite in user_favorites:
        if favorite.character_id:
            favorites_list.append({'type': 'character', 'id': favorite.character_id})
        elif favorite.planet_id:
            favorites_list.append({'type': 'planet', 'id': favorite.planet_id})

    return jsonify(favorites_list)

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    current_user_id = 1  # Simulated current user ID (replace with actual authentication)
    favorite = Favorite(user_id=current_user_id, planet_id=planet_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify({'message': 'Favorite planet added successfully'})

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    current_user_id = 1  # Simulated current user ID (replace with actual authentication)
    favorite = Favorite(user_id=current_user_id, character_id=people_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify({'message': 'Favorite character added successfully'})

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    current_user_id = 1  # Simulated current user ID (replace with actual authentication)
    favorite = Favorite.query.filter_by(user_id=current_user_id, planet_id=planet_id).first()

    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({'message': 'Favorite planet deleted successfully'})
    else:
        return jsonify({'error': 'Planet is not in favorites'}), 404

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    current_user_id = 1  # Simulated current user ID (replace with actual authentication)
    favorite = Favorite.query.filter_by(user_id=current_user_id, character_id=people_id).first()

    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({'message': 'Favorite character deleted successfully'})
    else:
        return jsonify({'error': 'Character is not in favorites'}), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)