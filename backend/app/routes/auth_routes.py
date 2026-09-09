from flask import Blueprint, request, jsonify
from app.controllers import auth_controller

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    result = auth_controller.register(data)
    return jsonify(result)

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    result = auth_controller.login(data)
    return jsonify(result)