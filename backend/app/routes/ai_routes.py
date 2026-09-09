from flask import Blueprint
from app.controllers.ai_controller import sales_forecast_controller

ai_bp = Blueprint("ai", __name__)

@ai_bp.route("/sales-forecast", methods=["GET"])
def sales_forecast():
    return sales_forecast_controller()