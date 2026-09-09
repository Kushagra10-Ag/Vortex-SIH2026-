from app.services.ai_service import get_sales_forecast
from flask import jsonify

def sales_forecast_controller():
    result = get_sales_forecast()
    return jsonify(result)