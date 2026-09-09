from flask import Blueprint, jsonify
from app.controllers.analytics_controller import analytics_controller
from app.controllers import analytics_controller as analytics_module

analytics_bp = Blueprint("analytics", __name__)

@analytics_bp.route("/total-sales", methods=["GET"])
def total_sales():
    return jsonify(analytics_module.get_total_sales())

@analytics_bp.route("/product-performance", methods=["GET"])
def product_performance():
    return jsonify(analytics_module.get_product_performance())

@analytics_bp.route("/dashboard", methods=["GET"])
def dashboard():
    return analytics_controller()