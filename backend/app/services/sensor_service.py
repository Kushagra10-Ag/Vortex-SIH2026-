from datetime import datetime, timedelta
from app.db import db
from app.models import SensorReading, Device, Alert
from sqlalchemy import func

def record_reading(data):
    sensor_id = data.get("sensor_id")
    sensor_type = data.get("sensor_type")
    value = data.get("value")

    if not sensor_id or not sensor_type or value is None:
        return {"error": "sensor_id, sensor_type, and value are required"}, 400

    try:
        val_float = float(value)
    except (ValueError, TypeError):
        return {"error": "value must be a numeric float"}, 400

    # Device lookup
    device_id = data.get("device_id")
    if not device_id and data.get("device_id_str"):
        dev = Device.query.filter_by(device_id=data.get("device_id_str")).first()
        if dev:
            device_id = dev.id

    threshold_min = data.get("threshold_min")
    threshold_max = data.get("threshold_max")

    is_anomaly = False
    if threshold_min is not None and val_float < float(threshold_min):
        is_anomaly = True
    if threshold_max is not None and val_float > float(threshold_max):
        is_anomaly = True

    reading = SensorReading(
        device_id=device_id,
        sensor_id_str=sensor_id,
        sensor_type=sensor_type,
        value=val_float,
        unit=data.get("unit", ""),
        location=data.get("location", "Store Floor"),
        threshold_min=threshold_min,
        threshold_max=threshold_max,
        is_anomaly=is_anomaly,
        timestamp=datetime.utcnow()
    )

    db.session.add(reading)

    # If anomaly, auto-generate an Alert
    alert_created = None
    if is_anomaly:
        alert = Alert(
            title=f"Sensor Anomaly: {sensor_type.capitalize()} ({sensor_id})",
            message=f"Reading {val_float} {data.get('unit', '')} exceeded normal thresholds [{threshold_min}, {threshold_max}] at {data.get('location', 'Store Floor')}.",
            severity="warning" if sensor_type != "temperature" else "critical",
            category="sensor_anomaly",
            source_device_id=device_id,
        )
        db.session.add(alert)
        alert_created = alert

    db.session.commit()

    res = {
        "message": "Sensor reading recorded successfully",
        "reading": reading.to_dict(),
        "is_anomaly": is_anomaly
    }
    if alert_created:
        res["alert_id"] = alert_created.id

    return res, 201


def get_latest_readings(sensor_type=None, limit=50):
    query = SensorReading.query
    if sensor_type:
        query = query.filter_by(sensor_type=sensor_type)

    readings = query.order_by(SensorReading.timestamp.desc()).limit(limit).all()
    return [r.to_dict() for r in readings]


def get_readings_history(sensor_id_str, hours=24):
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    readings = SensorReading.query.filter(
        SensorReading.sensor_id_str == sensor_id_str,
        SensorReading.timestamp >= cutoff
    ).order_by(SensorReading.timestamp.asc()).all()

    return [r.to_dict() for r in readings]


def get_sensor_summary():
    # Last 2 hours averages
    cutoff = datetime.utcnow() - timedelta(hours=2)

    avg_temp = db.session.query(func.avg(SensorReading.value)).filter(
        SensorReading.sensor_type == "temperature",
        SensorReading.timestamp >= cutoff
    ).scalar()

    avg_humidity = db.session.query(func.avg(SensorReading.value)).filter(
        SensorReading.sensor_type == "humidity",
        SensorReading.timestamp >= cutoff
    ).scalar()

    active_sensors_count = db.session.query(SensorReading.sensor_id_str).filter(
        SensorReading.timestamp >= cutoff
    ).distinct().count()

    anomalies_count = SensorReading.query.filter(
        SensorReading.is_anomaly == True,
        SensorReading.timestamp >= cutoff
    ).count()

    return {
        "avg_temperature": round(float(avg_temp), 1) if avg_temp is not None else None,
        "avg_humidity": round(float(avg_humidity), 1) if avg_humidity is not None else None,
        "active_sensors_count": active_sensors_count,
        "recent_anomalies_count": anomalies_count,
    }

