from app.services import sensor_service

def record_reading(data):
    return sensor_service.record_reading(data)


def get_latest_readings(sensor_type=None, limit=50):
    return sensor_service.get_latest_readings(sensor_type=sensor_type, limit=limit)


def get_sensor_history(sensor_id, hours=24):
    return sensor_service.get_readings_history(sensor_id, hours=hours)


def get_sensor_summary():
    return sensor_service.get_sensor_summary()

