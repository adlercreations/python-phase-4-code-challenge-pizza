#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


@app.route("/restaurants", methods=["GET"])
def all_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([restaurant.to_dict(rules=("-restaurant_pizzas",))
for restaurant in restaurants]), 200


@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant(id):
    restaurant = db.session.get(Restaurant, id)
    if restaurant:
        return jsonify(restaurant.to_dict(rules=("-restaurant_pizzas", "-restaurant_pizzas.restaurant", "-restaurant_pizzas.pizza"))), 200
    return jsonify({"error": "Restaurant not found"}), 404


@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    restaurant = db.session.get(Restaurant, id)
    if restaurant:
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204
    return jsonify({"error": "Restaurant not found"}), 404


@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([pizza.to_dict(rules=("-restaurant_pizzas",)) for pizza in pizzas]), 200


@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()
    price = data.get("price")

    if price is None or price < 1 or price > 30:
        return jsonify({"errors": ["validation errors"]}), 400
    
    restaurant_id = data.get("restaurant_id")
    pizza_id = data.get("pizza_id")

    restaurant = db.session.get(Restaurant, restaurant_id)
    pizza = db.session.get(Pizza, pizza_id)

    if not restaurant or not pizza:
        return jsonify({"errors": ["validation errors"]}), 400
    
    restaurant_pizza = RestaurantPizza(price=price, restaurant_id=restaurant_id, pizza_id=pizza_id)

    db.session.add(restaurant_pizza)
    db.session.commit()

    response_data = restaurant_pizza.to_dict()
    response_data["restaurant"] = restaurant.to_dict()
    response_data["pizza"] = pizza.to_dict()

    return jsonify(response_data), 201

@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404

if __name__ == "__main__":
    app.run(port=5555, debug=True)
