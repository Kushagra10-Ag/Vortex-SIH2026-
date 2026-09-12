from datetime import datetime
from sqlalchemy import desc

from app.db import db
from app.models import SensorReading, Device


# ==========================================================
# SAVE SENSOR READING
# ==========================================================

def save_sensor_reading(data):

    device = Device.query.filter_by(
        device_id=data["device_id"]
    ).first()

    if not device:
        raise ValueError("Device not found.")

    reading = SensorReading(
        device_id=device.id,
        sensor_id=data["sensor_id"],
        sensor_type=data["sensor_type"],
        value=data["value"],
        unit=data.get("unit"),
        is_mock=data.get("is_mock", False),
        is_anomaly=data.get("is_anomaly", False),
        threshold_min=data.get("threshold_min"),
        threshold_max=data.get("threshold_max"),
        created_at=datetime.utcnow()
    )

    db.session.add(reading)
    db.session.commit()

    return reading.to_dict()


# ==========================================================
# GET LATEST READINGS
# ==========================================================

def get_latest_readings(sensor_type=None, limit=20):

    query = SensorReading.query.order_by(
        desc(SensorReading.created_at)
    )
    if sensor_type:
        query = query.filter_by(sensor_type=sensor_type)
    readings = query.limit(limit).all()

    return [
        reading.to_dict()
        for reading in readings
    ]


# ==========================================================
# GET READINGS OF ONE SENSOR TYPE
# ==========================================================

def get_sensor_readings(sensor_type, limit=50):

    readings = SensorReading.query.filter_by(
        sensor_type=sensor_type
    ).order_by(
        desc(SensorReading.created_at)
    ).limit(limit).all()

    return [
        reading.to_dict()
        for reading in readings
    ]


# ==========================================================
# SENSOR HISTORY
# ==========================================================

def get_sensor_history(device_id):

    device = Device.query.filter_by(
        device_id=device_id
    ).first()

    if not device:
        raise ValueError("Device not found.")

    readings = SensorReading.query.filter_by(
        device_id=device.id
    ).order_by(
        desc(SensorReading.created_at)
    ).all()

    return [
        reading.to_dict()
        for reading in readings
    ]


# ==========================================================
# LATEST VALUE OF A SENSOR
# ==========================================================

def get_latest_sensor(sensor_type):

    reading = SensorReading.query.filter_by(
        sensor_type=sensor_type
    ).order_by(
        desc(SensorReading.created_at)
    ).first()

    if not reading:
        return None

    return reading.to_dict()


# ==========================================================
# DASHBOARD SUMMARY
# ==========================================================

def get_sensor_summary():

    total = SensorReading.query.count()

    latest = SensorReading.query.order_by(
        desc(SensorReading.created_at)
    ).all()

    summary = {}

    for reading in latest:

        if reading.sensor_type not in summary:

            summary[reading.sensor_type] = {
                "value": reading.value,
                "unit": reading.unit,
                "updated_at": reading.created_at
            }

    return {
        "total_readings": total,
        "sensors": summary
    }


# ==========================================================
# DELETE OLD DATA
# ==========================================================

def delete_old_readings(days=30):

    from datetime import timedelta

    threshold = datetime.utcnow() - timedelta(days=days)

    SensorReading.query.filter(
        SensorReading.created_at < threshold
    ).delete()

    db.session.commit()

    return {
        "message": "Old sensor readings deleted."
    }


def record_reading(data):
    return save_sensor_reading(data)


def get_readings_history(sensor_id, hours=24):
    from datetime import timedelta

    device = Device.query.filter_by(device_id=sensor_id).first()
    if not device:
        raise ValueError("Device not found.")

    threshold = datetime.utcnow() - timedelta(hours=hours)
    readings = SensorReading.query.filter(
        SensorReading.device_id == device.id,
        SensorReading.created_at >= threshold,
    ).order_by(desc(SensorReading.created_at)).all()
    return [reading.to_dict() for reading in readings]