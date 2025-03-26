# items.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from database import mysql  # تأكد أن الاستيراد صحيح

items = Blueprint('items', __name__, url_prefix='/api')  # تأكد أن هناك `url_prefix='/api'`

@items.route('/products', methods=['POST'])
@jwt_required()
def add_item():
    data = request.json
    name = data['name']
    description = data['description']
    price = data['price']
    quantity = data['quantity']

    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO products (name, description, price, quantity) VALUES (%s, %s, %s, %s)", 
                   (name, description, price, quantity))
    mysql.connection.commit()
    cursor.close()

    return jsonify({'message': 'Item added successfully'}), 201

@items.route('/products', methods=['GET'])
@jwt_required()
def get_items():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM products")
    items = cursor.fetchall()
    cursor.close()

    return jsonify(items)
