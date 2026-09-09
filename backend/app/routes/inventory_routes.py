from flask import Blueprint, request, jsonify
from app.controllers import inventory_controller

inventory_bp = Blueprint("inventory", __name__)

# Add Product
@inventory_bp.route("/add-product", methods=["POST"])
def add_product():
    data = request.get_json()
    result = inventory_controller.add_product(data)
    return jsonify(result)

# Get All Products
@inventory_bp.route("/products", methods=["GET"])
def get_products():
    result = inventory_controller.get_products()
    return jsonify(result)
@inventory_bp.route("/delete-product/<int:product_id>", methods=["DELETE"])
def delete_product_route(product_id):
    return inventory_controller.delete_product(product_id)
@inventory_bp.route("/update-product/<int:product_id>", methods=["PUT"])
def update_product_route(product_id):
    data = request.get_json()
    return inventory_controller.update_product(product_id, data)