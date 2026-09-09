from flask import jsonify


from app.services import analytics_service

def get_total_sales():
    return analytics_service.get_total_sales()

def get_product_performance():
    return analytics_service.get_product_performance()
def analytics_controller():
    return jsonify({
        "revenueTrend": analytics_service.get_revenue_trend(),
        "monthlySales": analytics_service.get_monthly_sales(),
        "categoryData": analytics_service.get_category_data(),
        "kpis": analytics_service.get_kpis(),
        "expiryRisk": analytics_service.get_expiry_risk()
    })