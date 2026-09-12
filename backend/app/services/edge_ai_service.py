from app.services.device_service import update_heartbeat
from app.services.sensor_service import add_sensor_reading
from app.services.monitoring_service import (
    save_camera_event,
    update_shelf_status,
    save_footfall
)
from app.services.alert_service import create_alert


# ==========================================================
# PROCESS CAMERA EVENT
# ==========================================================

def process_camera_event(data):

    update_heartbeat(data["device_id"])

    event = save_camera_event(data)

    event_type = data["event_type"]

    if event_type == "queue_detected":

        queue = data.get("details", {}).get("queue_length", 0)

        if queue >= 5:

            create_alert({

                "title": "Queue Overflow",

                "message": f"Queue length reached {queue}",

                "severity": "warning",

                "category": "camera",

                "device_id": data["device_id"]

            })

    elif event_type == "theft_alert":

        create_alert({

            "title": "Possible Theft",

            "message": "Suspicious activity detected.",

            "severity": "critical",

            "category": "camera",

            "device_id": data["device_id"]

        })

    elif event_type == "shelf_empty":

        create_alert({

            "title": "Shelf Empty",

            "message": "Camera detected an empty shelf.",

            "severity": "warning",

            "category": "inventory",

            "device_id": data["device_id"]

        })

    return event


# ==========================================================
# PROCESS SENSOR READING
# ==========================================================

def process_sensor_reading(data):

    update_heartbeat(data["device_id"])

    reading = add_sensor_reading(data)

    sensor = data["sensor_type"]

    value = data["value"]

    if sensor == "temperature":

        if value > 30:

            create_alert({

                "title": "High Temperature",

                "message": f"Temperature reached {value}°C",

                "severity": "critical",

                "category": "sensor",

                "device_id": data["device_id"]

            })

    elif sensor == "humidity":

        if value > 80:

            create_alert({

                "title": "High Humidity",

                "message": f"Humidity reached {value}%",

                "severity": "warning",

                "category": "sensor",

                "device_id": data["device_id"]

            })

    elif sensor == "ultrasonic":

        if value < 10:

            create_alert({

                "title": "Shelf Nearly Empty",

                "message": "Ultrasonic sensor detected low stock.",

                "severity": "warning",

                "category": "inventory",

                "device_id": data["device_id"]

            })

    return reading


# ==========================================================
# PROCESS SHELF STATUS
# ==========================================================

def process_shelf_status(data):

    update_heartbeat(data["device_id"])

    shelf = update_shelf_status(data)

    if shelf["status"] == "empty":

        create_alert({

            "title": "Shelf Empty",

            "message": "Immediate refill required.",

            "severity": "critical",

            "category": "inventory",

            "device_id": data["device_id"]

        })

    elif shelf["status"] == "low":

        create_alert({

            "title": "Shelf Running Low",

            "message": "Shelf stock is below threshold.",

            "severity": "warning",

            "category": "inventory",

            "device_id": data["device_id"]

        })

    return shelf


# ==========================================================
# PROCESS FOOTFALL
# ==========================================================

def process_footfall(data):

    update_heartbeat(data["device_id"])

    footfall = save_footfall(data)

    occupancy = (
        data.get("entry_count", 0)
        -
        data.get("exit_count", 0)
    )

    if occupancy >= 50:

        create_alert({

            "title": "Store Crowded",

            "message": f"Current occupancy: {occupancy}",

            "severity": "warning",

            "category": "queue",

            "device_id": data["device_id"]

        })

    return footfall


# ==========================================================
# UNIVERSAL EDGE AI ENTRY POINT
# ==========================================================

def process_edge_payload(payload):

    payload_type = payload.get("type")

    if payload_type == "camera":

        return process_camera_event(payload)

    elif payload_type == "sensor":

        return process_sensor_reading(payload)

    elif payload_type == "shelf":

        return process_shelf_status(payload)

    elif payload_type == "footfall":

        return process_footfall(payload)

    else:

        raise ValueError("Unknown Edge AI payload type.")