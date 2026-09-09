from flask import Blueprint, request, jsonify
from app.controllers import chatbot_controller

chatbot_bp = Blueprint("chatbot", __name__)

@chatbot_bp.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    return jsonify(chatbot_controller.get_response(data))