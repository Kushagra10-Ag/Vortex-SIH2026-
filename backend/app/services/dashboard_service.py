from datetime import datetime, timedelta
from app.db import db
from app.models import Product, Bill, Device, ShelfStatus, Footfall, Alert, CameraEvent, SensorReading
from sqlalchemy import func

def get_dashboard_overview():
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # 1. Retail Sales & Stock KPIs
    total_sales_val = db.session.query(func.sum(Bill.total_amount)).scalar() or 0.0
    today_sales_val = db.session.query(func.sum(Bill.total_amount)).filter(Bill.created_at >= today_start).scalar() or 0.0
    total_bills_count = Bill.query.count()
    total_products_count = Product.query.count()
    low_stock_products_count = Product.query.filter(Product.quantity <= Product.min_stock_level).count()

    # 2. IoT Fleet KPIs
    total_devices = Device.query.count()
    online_devices = Device.query.filter_by(status="online").count()

    # 3. Shelf Health
    total_shelves = ShelfStatus.query.count()
    avg_shelf_fill = db.session.query(func.avg(ShelfStatus.fill_percentage)).scalar() or 0.0
    empty_shelves = ShelfStatus.query.filter_by(status="empty").count()

    # 4. Footfall
    today_entries = db.session.query(func.sum(Footfall.entry_count)).filter(Footfall.timestamp >= today_start).scalar() or 0
    latest_footfall = Footfall.query.order_by(Footfall.timestamp.desc()).first()
    live_occupancy = latest_footfall.current_occupancy if latest_footfall else 0

    # 5. Alerts Summary
    open_alerts = Alert.query.filter_by(is_resolved=False).count()
    critical_alerts = Alert.query.filter_by(is_resolved=False, severity="critical").count()

    # 6. Recent Activity Feed (latest 5 alerts + latest 5 camera events)
    recent_alerts = Alert.query.order_by(Alert.created_at.desc()).limit(5).all()
    recent_camera_events = CameraEvent.query.order_by(CameraEvent.timestamp.desc()).limit(5).all()

    return {
        "timestamp": now.isoformat(),
        "kpis": {
            "total_revenue": round(float(total_sales_val), 2),
            "today_revenue": round(float(today_sales_val), 2),
            "total_bills": total_bills_count,
            "total_products": total_products_count,
            "low_stock_products": low_stock_products_count,
        },
        "iot_fleet": {
            "total": total_devices,
            "online": online_devices,
            "offline": max(0, total_devices - online_devices),
        },
        "smart_shelves": {
            "total_shelves": total_shelves,
            "avg_fill_percentage": round(float(avg_shelf_fill), 1),
            "empty_shelves": empty_shelves,
        },
        "footfall": {
            "today_visitors": int(today_entries),
            "current_occupancy": int(live_occupancy),
        },
        "alerts_overview": {
            "open": open_alerts,
            "critical": critical_alerts,
        },
        "recent_activity": {
            "alerts": [a.to_dict() for a in recent_alerts],
            "camera_events": [c.to_dict() for c in recent_camera_events],
        }
    }


def get_realtime_telemetry():
    now = datetime.utcnow()
    cutoff_10m = now - timedelta(minutes=10)

    # Latest readings per sensor type
    sensor_types = ["temperature", "humidity", "weight"]
    latest_sensors = {}
    for stype in sensor_types:
        r = SensorReading.query.filter_by(sensor_type=stype).order_by(SensorReading.timestamp.desc()).first()
        latest_sensors[stype] = r.to_dict() if r else None

    # Latest camera detection
    latest_camera = CameraEvent.query.order_by(CameraEvent.timestamp.desc()).first()

    # Latest footfall
    latest_footfall = Footfall.query.order_by(Footfall.timestamp.desc()).first()

    return {
        "timestamp": now.isoformat(),
        "live_sensors": latest_sensors,
        "latest_camera_event": latest_camera.to_dict() if latest_camera else None,
        "current_store_occupancy": latest_footfall.current_occupancy if latest_footfall else 0,
    }

