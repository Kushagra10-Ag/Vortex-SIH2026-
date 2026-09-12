from app.services import sensor_service
from app.utils.validators import validate_sensor_reading

def record_reading(data):
    valid, error = validate_sensor_reading(data)
    if not valid:
        return {"success": False, "error": error}, 400
    return sensor_service.record_reading(data), 201


def get_latest_readings(sensor_type=None, limit=50):
    return sensor_service.get_latest_readings(sensor_type=sensor_type, limit=limit)


def get_sensor_history(sensor_id, hours=24):
    return sensor_service.get_readings_history(sensor_id, hours=hours)


def get_sensor_summary():
    return sensor_service.get_sensor_summary()

