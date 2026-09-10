from datetime import datetime, timedelta
from app.db import db
from app.models import Device, CameraEvent, ShelfStatus, Footfall, Alert, Product
from sqlalchemy import func

def get_realtime_status():
    cutoff_active = datetime.utcnow() - timedelta(minutes=10)

    # Active / total devices
    total_devices = Device.query.count()
    online_devices = Device.query.filter(
        (Device.status == "online") | (Device.last_heartbeat >= cutoff_active)
    ).count()

    # Active cameras
    total_cameras = Device.query.filter_by(device_type="camera").count()
    online_cameras = Device.query.filter(
        Device.device_type == "camera",
        (Device.status == "online") | (Device.last_heartbeat >= cutoff_active)
    ).count()

    # Shelves health
    total_shelves = ShelfStatus.query.count()
    low_stock_shelves = ShelfStatus.query.filter(ShelfStatus.status.in_(["low_stock", "empty"])).count()
    avg_shelf_fill = db.session.query(func.avg(ShelfStatus.fill_percentage)).scalar() or 0.0

    # Footfall today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_footfall = db.session.query(func.sum(Footfall.entry_count)).filter(
        Footfall.timestamp >= today_start
    ).scalar() or 0

    latest_occupancy_record = Footfall.query.order_by(Footfall.timestamp.desc()).first()
    current_occupancy = latest_occupancy_record.current_occupancy if latest_occupancy_record else 0

    # Unresolved critical / warning alerts
    open_alerts_count = Alert.query.filter_by(is_resolved=False).count()
    critical_alerts_count = Alert.query.filter_by(is_resolved=False, severity="critical").count()

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "devices": {
            "total": total_devices,
            "online": online_devices,
            "offline": max(0, total_devices - online_devices),
        },
        "cameras": {
            "total": total_cameras,
            "online": online_cameras,
        },
        "shelves": {
            "total": total_shelves,
            "needs_restock": low_stock_shelves,
            "avg_fill_percentage": round(float(avg_shelf_fill), 1),
        },
        "footfall": {
            "today_entries": int(today_footfall),
            "current_occupancy": int(current_occupancy),
        },
        "alerts": {
            "total_open": open_alerts_count,
            "critical": critical_alerts_count,
        }
    }


def record_camera_event(data):
    camera_id = data.get("camera_id") or data.get("camera_id_str")
    event_type = data.get("event_type")

    if not camera_id or not event_type:
        return {"error": "camera_id and event_type are required"}, 400

    device_id = data.get("device_id")
    if not device_id:
        dev = Device.query.filter_by(device_id=camera_id).first()
        if dev:
            device_id = dev.id

    event = CameraEvent(
        device_id=device_id,
        camera_id_str=camera_id,
        event_type=event_type,
        confidence=float(data.get("confidence", 0.95)),
        snapshot_url=data.get("snapshot_url", ""),
        bbox_coordinates=data.get("bbox_coordinates", []),
        details=data.get("details", {}),
        timestamp=datetime.utcnow()
    )

    db.session.add(event)

    # Auto alert on high-severity vision events
    if event_type in ["theft_alert", "queue_overflow"]:
        alert = Alert(
            title=f"Security Alert: {event_type.replace('_', ' ').title()}",
            message=f"Camera {camera_id} reported {event_type} with confidence {event.confidence:.2f}.",
            severity="critical" if event_type == "theft_alert" else "warning",
            category="theft_security",
            source_device_id=device_id
        )
        db.session.add(alert)
    elif event_type == "out_of_stock_detected":
        shelf_ref = (data.get("details") or {}).get("shelf_code", "Shelf")
        alert = Alert(
            title=f"Shelf Out-Of-Stock: {shelf_ref}",
            message=f"Vision detector spotted empty shelf at {shelf_ref}.",
            severity="warning",
            category="shelf_stock",
            source_device_id=device_id
        )
        db.session.add(alert)

    db.session.commit()
    return {"message": "Camera event logged", "event": event.to_dict()}, 201


def get_camera_events(limit=50, event_type=None):
    query = CameraEvent.query
    if event_type:
        query = query.filter_by(event_type=event_type)

    events = query.order_by(CameraEvent.timestamp.desc()).limit(limit).all()
    return [e.to_dict() for e in events]


def get_shelf_statuses():
    shelves = ShelfStatus.query.order_by(ShelfStatus.shelf_code.asc()).all()
    return [s.to_dict() for s in shelves]


def update_shelf_status(shelf_id, data):
    shelf = ShelfStatus.query.get(shelf_id)
    if not shelf:
        shelf = ShelfStatus.query.filter_by(shelf_code=str(shelf_id)).first()

    if not shelf:
        return {"error": "Shelf not found"}, 404

    if "current_stock_estimate" in data:
        shelf.current_stock_estimate = int(data["current_stock_estimate"])
    if "capacity" in data:
        shelf.capacity = int(data["capacity"])
    if "section" in data:
        shelf.section = data["section"]
    if "product_id" in data:
        shelf.product_id = data["product_id"]

    # Recalculate fill percentage & status
    if shelf.capacity > 0:
        shelf.fill_percentage = min(100.0, max(0.0, (shelf.current_stock_estimate / shelf.capacity) * 100.0))

    if shelf.current_stock_estimate == 0:
        shelf.status = "empty"
    elif shelf.fill_percentage < 25.0:
        shelf.status = "low_stock"
    else:
        shelf.status = data.get("status", "normal")

    shelf.last_checked = datetime.utcnow()
    db.session.commit()

    return {"message": "Shelf status updated", "shelf": shelf.to_dict()}, 200


def record_footfall(data):
    entry_count = int(data.get("entry_count", 0))
    exit_count = int(data.get("exit_count", 0))
    area_name = data.get("area_name", "Main Entrance")

    # Fetch last known occupancy to calculate new occupancy
    last_record = Footfall.query.filter_by(area_name=area_name).order_by(Footfall.timestamp.desc()).first()
    prev_occupancy = last_record.current_occupancy if last_record else 0
    current_occupancy = max(0, prev_occupancy + entry_count - exit_count)

    now = datetime.utcnow()
    hourly_bucket = now.strftime("%Y-%m-%d %H:00")

    footfall = Footfall(
        device_id=data.get("device_id"),
        area_name=area_name,
        entry_count=entry_count,
        exit_count=exit_count,
        current_occupancy=current_occupancy,
        dwell_time_avg_seconds=float(data.get("dwell_time_avg_seconds", 0.0)),
        hourly_bucket=hourly_bucket,
        timestamp=now
    )

    db.session.add(footfall)
    db.session.commit()

    return {"message": "Footfall logged", "footfall": footfall.to_dict()}, 201


def get_footfall_analytics(timeframe="today"):
    now = datetime.utcnow()
    if timeframe == "today":
        cutoff = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif timeframe == "week":
        cutoff = now - timedelta(days=7)
    else:
        cutoff = now - timedelta(hours=24)

    records = Footfall.query.filter(Footfall.timestamp >= cutoff).order_by(Footfall.timestamp.asc()).all()

    total_in = sum(r.entry_count for r in records)
    total_out = sum(r.exit_count for r in records)
    current_occ = records[-1].current_occupancy if records else 0

    # Hourly buckets breakdown
    buckets = {}
    for r in records:
        b = r.hourly_bucket or r.timestamp.strftime("%H:00")
        if b not in buckets:
            buckets[b] = {"entries": 0, "exits": 0, "avg_occupancy": []}
        buckets[b]["entries"] += r.entry_count
        buckets[b]["exits"] += r.exit_count
        buckets[b]["avg_occupancy"].append(r.current_occupancy)

    hourly_breakdown = [
        {
            "hour": b,
            "entries": stats["entries"],
            "exits": stats["exits"],
            "avg_occupancy": round(sum(stats["avg_occupancy"]) / len(stats["avg_occupancy"]), 1) if stats["avg_occupancy"] else 0
        }
        for b, stats in sorted(buckets.items())
    ]

    return {
        "timeframe": timeframe,
        "total_entries": total_in,
        "total_exits": total_out,
        "current_occupancy": current_occ,
        "hourly_breakdown": hourly_breakdown
    }

