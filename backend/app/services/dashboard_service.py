from sqlalchemy import func
from app.models import (
    Product,
    Bill,
    Alert,
    Device,
    SensorReading,
    CameraEvent,
    ShelfStatus,
    Footfall,
)
from app.services.device_service import update_offline_devices
from flask import current_app


def _serialize(obj):
    """Safely convert a model instance to a dict, even for models
    (like SensorReading right now) that don't define to_dict() yet."""
    if obj is None:
        return None
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


# ==========================================================
# DASHBOARD OVERVIEW
# ==========================================================

def get_dashboard_overview():

    update_offline_devices(current_app.config.get("DEVICE_OFFLINE_TIMEOUT_MINUTES", 5))

    total_products = Product.query.count()

    total_devices = Device.query.count()
    online_devices = Device.query.filter_by(status="online").count()
    offline_devices = Device.query.filter_by(status="offline").count()

    total_sales = (
        Bill.query.with_entities(
            func.coalesce(func.sum(Bill.total_amount), 0)
        ).scalar()
    )

    total_bills = Bill.query.count()

    low_stock = Product.query.filter(
        Product.quantity <= Product.min_stock_level
    ).count()

    out_of_stock = Product.query.filter(
        Product.quantity <= 0
    ).count()

    unread_alerts = Alert.query.filter_by(is_read=False).count()

    critical_alerts = Alert.query.filter_by(
        severity="critical",
        is_resolved=False
    ).count()

    latest_sensor = SensorReading.query.order_by(
        SensorReading.created_at.desc()
    ).first()

    latest_camera = CameraEvent.query.order_by(
        CameraEvent.created_at.desc()
    ).first()

    return {
        "sales": {
            "total_sales": float(total_sales),
            "total_bills": total_bills,
        },

        "inventory": {
            "products": total_products,
            "low_stock": low_stock,
            "out_of_stock": out_of_stock,
        },

        "devices": {
            "total": total_devices,
            "online": online_devices,
            "offline": offline_devices,
        },

        "alerts": {
            "critical": critical_alerts,
            "unread": unread_alerts,
        },

        "latest_sensor": _serialize(latest_sensor),
        "latest_camera_event": _serialize(latest_camera),
    }


# ==========================================================
# LIVE TELEMETRY
# ==========================================================

def get_realtime_telemetry():

    sensors = SensorReading.query.order_by(
        SensorReading.created_at.desc()
    ).limit(10).all()

    camera_events = CameraEvent.query.order_by(
        CameraEvent.created_at.desc()
    ).limit(10).all()

    shelves = ShelfStatus.query.all()

    footfall = Footfall.query.order_by(
        Footfall.created_at.desc()
    ).first()

    return {
        "sensor_readings": [_serialize(s) for s in sensors],
        "camera_events": [_serialize(c) for c in camera_events],
        "shelf_status": [_serialize(s) for s in shelves],
        "footfall": _serialize(footfall),
    }


# ==========================================================
# DEVICE SUMMARY
# ==========================================================

def get_device_summary():
    return [_serialize(d) for d in Device.query.all()]


# ==========================================================
# INVENTORY SUMMARY
# ==========================================================

def get_inventory_summary():

    healthy = Product.query.filter(
        Product.quantity > Product.min_stock_level
    ).count()

    low = Product.query.filter(
        Product.quantity <= Product.min_stock_level,
        Product.quantity > 0
    ).count()

    empty = Product.query.filter(
        Product.quantity <= 0
    ).count()

    return {
        "healthy": healthy,
        "low_stock": low,
        "out_of_stock": empty,
    }


# ==========================================================
# RECENT ALERTS
# ==========================================================

def get_recent_alerts(limit=5):
    alerts = Alert.query.order_by(
        Alert.created_at.desc()
    ).limit(limit).all()

    return [_serialize(a) for a in alerts]
from datetime import date, timedelta
from sqlalchemy import func

# Adjust this import to wherever your SQLAlchemy `db` instance actually lives
# (commonly app.extensions, app.models, or app itself).
from app import db


OPEN_HOUR, CLOSE_HOUR = 9, 21  # store hours used to build hourly series


def _hour_range():
    return list(range(OPEN_HOUR, CLOSE_HOUR + 1))


def _hourly_bill_stats_today():
    """Returns {hour: {"count": int, "revenue": float}} for today's bills."""
    today = date.today()
    rows = (
        db.session.query(
            func.extract("hour", Bill.created_at).label("hour"),
            func.count(Bill.id).label("cnt"),
            func.coalesce(func.sum(Bill.total_amount), 0).label("revenue"),
        )
        .filter(func.date(Bill.created_at) == today)
        .group_by("hour")
        .all()
    )
    return {int(r.hour): {"count": r.cnt, "revenue": float(r.revenue)} for r in rows}


def _hourly_footfall_today():
    """Returns {hour: visits} for today, from the Footfall table.
    'Footfall' here = entries (people walking in), since that's what the
    KPI card and hourly trend are meant to represent. Exits are also
    summed separately below in case you want net occupancy later."""
    today = date.today()
    rows = (
        db.session.query(
            func.extract("hour", Footfall.created_at).label("hour"),
            func.coalesce(func.sum(Footfall.entry_count), 0).label("entries"),
            func.coalesce(func.sum(Footfall.exit_count), 0).label("exits"),
        )
        .filter(func.date(Footfall.created_at) == today)
        .group_by("hour")
        .all()
    )
    return {
        int(r.hour): {"entries": int(r.entries), "exits": int(r.exits)}
        for r in rows
    }


def get_sales_trend(days=7):
    """Revenue per day for the last `days` days, Mon..Sun ordered."""
    start = date.today() - timedelta(days=days - 1)
    rows = (
        db.session.query(
            func.date(Bill.created_at).label("day"),
            func.coalesce(func.sum(Bill.total_amount), 0).label("revenue"),
        )
        .filter(func.date(Bill.created_at) >= start)
        .group_by("day")
        .all()
    )
    by_day = {r.day: float(r.revenue) for r in rows}

    day_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    series = []
    for i in range(days):
        d = start + timedelta(days=i)
        series.append({"label": day_labels[d.weekday()], "value": by_day.get(d, 0.0)})
    return series


def get_footfall_trend():
    footfall_by_hour = _hourly_footfall_today()
    return [
        {"label": str(hr), "value": footfall_by_hour.get(hr, 0)}
        for hr in _hour_range()
    ]


def get_queue_trend():
    """No dedicated queue-length sensor table exists yet, so this is
    estimated from bill throughput per hour as a proxy. Replace with a
    real query once you have queue/wait-time sensor data."""
    bill_stats = _hourly_bill_stats_today()
    series = []
    for hr in _hour_range():
        cnt = bill_stats.get(hr, {}).get("count", 0)
        series.append({"label": str(hr), "value": round(cnt * 1.4)})
    return series


def _alert_to_card(alert_dict):
    """Normalizes an Alert row into {title, sub, color} for direct display.
    Adjust the .get() keys to match your Alert model's actual columns."""
    severity = (alert_dict.get("severity") or "info").lower()
    color_map = {"critical": "red", "warning": "amber", "info": "blue"}
    return {
        "title": alert_dict.get("title") or alert_dict.get("type") or "Alert",
        "sub": alert_dict.get("message") or alert_dict.get("description") or "",
        "color": color_map.get(severity, "blue"),
    }


def get_recommendations(low_stock_products, peak_queue, busiest_hour):
    recs = []
    if low_stock_products:
        p = low_stock_products[0]
        recs.append({"icon": "refresh", "text": f"Restock {p['name']}"})
    if peak_queue >= 3:
        recs.append({"icon": "users", "text": "Open a second counter to cut queue"})
    if busiest_hour is not None:
        recs.append({"icon": "clock", "text": f"Peak traffic around {busiest_hour}:00"})
    if len(recs) < 4:
        recs.append({"icon": "chart", "text": "Demand trending up vs. yesterday"})
    return recs[:4]


def get_full_dashboard():
    """Single aggregated payload: everything the dashboard screen needs,
    fully computed server-side."""

    today = date.today()

    # ---- KPIs ----
    today_bills = Bill.query.filter(func.date(Bill.created_at) == today).all()
    today_revenue = sum(b.total_amount or 0 for b in today_bills)
    current_customers = len({b.customer_name or b.id for b in today_bills})

    products = Product.query.all()
    healthy = [p for p in products if p.quantity >= p.min_stock_level]
    low_stock = [p for p in products if p.quantity < p.min_stock_level and p.quantity > 0]
    critical = [p for p in products if p.quantity <= 0]
    inv_health_pct = round((len(healthy) / len(products)) * 100) if products else 100

    footfall_trend = get_footfall_trend()
    today_footfall = sum(x["value"] for x in footfall_trend)

    queue_trend = get_queue_trend()
    peak_queue = max((x["value"] for x in queue_trend), default=0)
    avg_wait = max(1, round(peak_queue * 1.5))

    unread_alerts = Alert.query.filter_by(is_read=False).count()
    critical_alerts = Alert.query.filter_by(severity="critical", is_resolved=False).count()

    # ---- busiest hour, for recommendations ----
    bill_stats = _hourly_bill_stats_today()
    busiest_hour = max(bill_stats, key=lambda h: bill_stats[h]["count"], default=None) \
        if bill_stats else None

    # ---- devices ----
    devices = [
        {"name": getattr(d, "name", f"Device {d.id}"), "status": getattr(d, "status", "offline")}
        for d in Device.query.all()
    ]

    # ---- recent alerts, normalized for direct display ----
    recent_alerts_raw = [
        _serialize(a) for a in Alert.query.order_by(Alert.created_at.desc()).limit(5).all()
    ]
    recent_alerts = [_alert_to_card(a) for a in recent_alerts_raw]

    low_stock_payload = [{"name": p.name, "quantity": p.quantity} for p in low_stock]

    return {
        "kpis": {
            "today_revenue": float(today_revenue),
            "current_customers": current_customers,
            "today_footfall": today_footfall,
            "inventory_health_pct": inv_health_pct,
            "avg_wait_minutes": avg_wait,
            "active_alerts": unread_alerts + critical_alerts,
        },
        "charts": {
            "sales_trend": get_sales_trend(days=7),
            "footfall_trend": footfall_trend,
            "queue_trend": queue_trend,
            "inventory_breakdown": {
                "healthy": len(healthy),
                "low_stock": len(low_stock),
                "critical": len(critical),
            },
        },
        "recent_alerts": recent_alerts,
        "recommendations": get_recommendations(low_stock_payload, peak_queue, busiest_hour),
        "devices": devices,
    }