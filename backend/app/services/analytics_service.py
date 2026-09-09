from app.models import Bill, BillItem
from app.db import db
from sqlalchemy import func
from sqlalchemy import text
from datetime import datetime

def get_total_sales():
    result = db.session.execute(text("SELECT SUM(total_amount) FROM bills")).scalar()
    return {"total_sales": float(result or 0)}


def get_total_profit():
    profit = db.session.query(
        func.sum((BillItem.selling_price - BillItem.cost_price) * BillItem.quantity)
    ).scalar()

    return {"total_profit": float(profit or 0)}


def get_product_performance():
    data = db.session.query(
        BillItem.product_name,
        func.sum(BillItem.quantity).label("total_sold")
    ).group_by(BillItem.product_name).all()

    return [
        {"product": d[0], "sold": int(d[1])}
        for d in data
    ]
def get_top_product():
    result = db.session.execute(text("""
        SELECT product_name, SUM(quantity) as total
        FROM bill_items
        GROUP BY product_name
        ORDER BY total DESC
        LIMIT 1
    """)).fetchone()

    return {
        "product": result[0],
        "quantity": result[1]
    }
def get_ai_insights():
    insights = []

    total_sales = db.session.execute(text("SELECT SUM(total_amount) FROM bills")).scalar()

    if total_sales and total_sales > 5000:
        insights.append("Sales are performing well 📈")

    low_stock = db.session.execute(text("""
        SELECT name FROM products WHERE quantity < min_stock_level
    """)).fetchall()

    if low_stock:
        insights.append("Some products are low in stock ⚠️")

    return insights
def get_revenue_trend():
    result = db.session.execute(text("""
        SELECT DATE(created_at) as date,
        SUM(total_amount) as revenue
        FROM bills
        GROUP BY DATE(created_at)
        ORDER BY date
    """)).fetchall()

    return [
        {"label": str(r[0]), "value": float(r[1])}
        for r in result
    ]
def get_monthly_sales():
    result = db.session.execute(text("""
        SELECT TO_CHAR(created_at, 'Mon') as month,
        SUM(total_amount) as total
        FROM bills
        GROUP BY month
        ORDER BY MIN(created_at)
    """)).fetchall()

    return [
        {"label": r[0], "value": float(r[1])}
        for r in result
    ]
def get_category_data():
    result = db.session.execute(text("""
        SELECT category, SUM(quantity) as total
        FROM bill_items
        GROUP BY category
    """)).fetchall()

    return [
        {"label": r[0], "value": int(r[1])}
        for r in result
    ]
def get_kpis():
    total = db.session.execute(text("SELECT SUM(total_amount) FROM bills")).scalar()

    avg = db.session.execute(text("""
        SELECT AVG(daily_total) FROM (
            SELECT SUM(total_amount) as daily_total
            FROM bills
            GROUP BY DATE(created_at)
        ) sub
    """)).scalar()

    top = db.session.execute(text("""
        SELECT product_name, SUM(quantity) as total
        FROM bill_items
        GROUP BY product_name
        ORDER BY total DESC
        LIMIT 1
    """)).fetchone()

    return {
        "totalRevenue": float(total or 0),
        "avgDaily": float(avg or 0),
        "topProduct": top[0] if top else "",
        "growth": 12.5  # static or calculate later
    }
def get_expiry_risk():
    result = db.session.execute(text("""
        SELECT name, expiry_date
        FROM products
        WHERE expiry_date IS NOT NULL
        AND expiry_date < NOW() + INTERVAL '10 days'
    """)).fetchall()

    return [
        {
            "name": r[0],
            "days": (r[1] - datetime.now().date()).days
        }
        for r in result
    ]