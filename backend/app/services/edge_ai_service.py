"""
Edge AI Service — Vision metadata processing, sensor anomaly classification,
and IoT sensor fusion for smart kirana retail.
"""
from datetime import datetime
from app.db import db
from app.models import ShelfStatus, Alert, CameraEvent

def process_vision_frame_metadata(camera_id, payload):
    """
    Process metadata sent from edge vision devices (e.g., YOLO/MobileNet inference running on Jetson/Raspberry Pi).
    """
    detections = payload.get("detections", [])
    shelf_id = payload.get("shelf_id")
    frame_timestamp = payload.get("timestamp") or datetime.utcnow().isoformat()

    person_count = 0
    empty_slots = 0
    suspicious_events = []

    for det in detections:
        label = det.get("label", "").lower()
        confidence = float(det.get("confidence", 0.0))

        if label in ["person", "customer"]:
            person_count += 1
        elif "empty" in label or "out_of_stock" in label:
            empty_slots += 1
        elif "theft" in label or "suspicious" in label:
            suspicious_events.append(det)

    analysis_result = {
        "camera_id": camera_id,
        "processed_at": frame_timestamp,
        "detected_persons": person_count,
        "empty_slots_detected": empty_slots,
        "alerts_generated": []
    }

    # If crowd congestion detected (> 15 people in small Kirana area)
    if person_count > 15:
        alert = Alert(
            title="Crowd Surge Detected",
            message=f"Camera {camera_id} detected {person_count} people in store area.",
            severity="warning",
            category="footfall_surge"
        )
        db.session.add(alert)
        analysis_result["alerts_generated"].append("crowd_surge")

    # If empty slot detected on assigned shelf
    if empty_slots > 0 and shelf_id:
        shelf = ShelfStatus.query.filter_by(shelf_code=shelf_id).first()
        if shelf:
            shelf.status = "low_stock" if shelf.current_stock_estimate > 0 else "empty"
            shelf.last_checked = datetime.utcnow()
            analysis_result["shelf_updated"] = shelf.shelf_code

    db.session.commit()
    return analysis_result


def detect_sensor_anomalies(sensor_type, value, history=None):
    """
    Statistical Z-Score / threshold check for sensor anomalies.
    """
    try:
        val = float(value)
    except (ValueError, TypeError):
        return {"is_anomaly": True, "reason": "Invalid numerical reading"}

    # Default Kirana store hardware thresholds
    thresholds = {
        "temperature": {"min": 10.0, "max": 38.0},  # Deep freeze or ambient room
        "humidity": {"min": 20.0, "max": 85.0},
        "weight": {"min": 0.0, "max": 100.0},
    }

    rule = thresholds.get(sensor_type)
    if rule:
        if val < rule["min"]:
            return {"is_anomaly": True, "reason": f"Value {val} below minimum threshold {rule['min']}"}
        if val > rule["max"]:
            return {"is_anomaly": True, "reason": f"Value {val} above maximum threshold {rule['max']}"}

    # Statistical outlier check if history provided
    if history and len(history) >= 5:
        mean_val = sum(history) / len(history)
        variance = sum((x - mean_val) ** 2 for x in history) / len(history)
        std_dev = variance ** 0.5
        if std_dev > 0.001:
            z_score = abs(val - mean_val) / std_dev
            if z_score > 3.0:
                return {"is_anomaly": True, "reason": f"Z-Score outlier ({z_score:.2f} standard deviations from mean)"}

    return {"is_anomaly": False, "reason": "Reading within expected range"}


def estimate_shelf_stock(shelf_code, weight_reading_kg, unit_item_weight_kg=0.25):
    """
    Estimate number of items on a smart shelf based on load-cell weight reading.
    """
    if unit_item_weight_kg <= 0:
        return 0

    estimated_units = max(0, int(round(weight_reading_kg / unit_item_weight_kg)))
    shelf = ShelfStatus.query.filter_by(shelf_code=shelf_code).first()

    if shelf:
        shelf.current_stock_estimate = estimated_units
        if shelf.capacity > 0:
            shelf.fill_percentage = min(100.0, round((estimated_units / shelf.capacity) * 100.0, 1))
        shelf.status = "empty" if estimated_units == 0 else ("low_stock" if shelf.fill_percentage < 25.0 else "normal")
        shelf.last_checked = datetime.utcnow()
        db.session.commit()

    return {
        "shelf_code": shelf_code,
        "weight_reading_kg": weight_reading_kg,
        "estimated_units": estimated_units,
        "shelf_status": shelf.status if shelf else "unknown"
    }

