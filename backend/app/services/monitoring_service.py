from datetime import datetime

from sqlalchemy import desc

from app.db import db
from app.models import (
    Device,
    CameraEvent,
    ShelfStatus,
    Footfall,
    Product,
)


# ==========================================================
# CAMERA EVENTS
# ==========================================================

def save_camera_event(data):

    device = Device.query.filter_by(
        device_id=data["device_id"]
    ).first()

    if not device:
        raise ValueError("Device not found.")

    event = CameraEvent(
        device_id=device.id,
        event_type=data["event_type"],
        confidence=data.get("confidence", 1.0),
        details=data.get("details", {}),
        created_at=datetime.utcnow()
    )

    db.session.add(event)
    db.session.commit()

    return event.to_dict()


def get_recent_camera_events(limit=20):

    events = CameraEvent.query.order_by(
        desc(CameraEvent.created_at)
    ).limit(limit).all()

    return [
        event.to_dict()
        for event in events
    ]


# ==========================================================
# SHELF STATUS
# ==========================================================

def save_shelf_status(data):

    product = Product.query.get(
        data["product_id"]
    )

    if not product:
        raise ValueError("Product not found.")

    device = Device.query.filter_by(
        device_id=data["device_id"]
    ).first()

    if not device:
        raise ValueError("Device not found.")

    shelf = ShelfStatus.query.filter_by(
        product_id=product.id
    ).first()

    if shelf:

        shelf.device_id = device.id
        shelf.estimated_quantity = data["estimated_quantity"]
        shelf.confidence = data.get("confidence", 1.0)
        shelf.status = data.get("status", "normal")
        shelf.last_checked = datetime.utcnow()

    else:

        shelf = ShelfStatus(
            product_id=product.id,
            device_id=device.id,
            estimated_quantity=data["estimated_quantity"],
            confidence=data.get("confidence", 1.0),
            status=data.get("status", "normal"),
            last_checked=datetime.utcnow()
        )

        db.session.add(shelf)

    db.session.commit()

    return shelf.to_dict()


def get_all_shelves():

    shelves = ShelfStatus.query.order_by(
        ShelfStatus.id
    ).all()

    return [
        shelf.to_dict()
        for shelf in shelves
    ]


def get_low_stock_shelves():

    shelves = ShelfStatus.query.filter(
        ShelfStatus.status.in_(
            ["low", "empty"]
        )
    ).all()

    return [
        shelf.to_dict()
        for shelf in shelves
    ]


# ==========================================================
# FOOTFALL
# ==========================================================

def save_footfall(data):

    device = Device.query.filter_by(
        device_id=data["device_id"]
    ).first()

    if not device:
        raise ValueError("Device not found.")

    footfall = Footfall(
        device_id=device.id,
        entry_count=data.get("entry_count", 0),
        exit_count=data.get("exit_count", 0),
        created_at=datetime.utcnow()
    )

    db.session.add(footfall)
    db.session.commit()

    return footfall.to_dict()


def get_recent_footfall(limit=24):

    records = Footfall.query.order_by(
        desc(Footfall.created_at)
    ).limit(limit).all()

    return [
        record.to_dict()
        for record in records
    ]


def get_total_footfall():

    records = Footfall.query.all()

    entries = sum(
        r.entry_count
        for r in records
    )

    exits = sum(
        r.exit_count
        for r in records
    )

    return {
        "entries": entries,
        "exits": exits,
        "occupancy": entries - exits
    }


# ==========================================================
# LIVE DASHBOARD
# ==========================================================

def get_live_monitoring():

    latest_event = CameraEvent.query.order_by(
        desc(CameraEvent.created_at)
    ).first()

    latest_footfall = Footfall.query.order_by(
        desc(Footfall.created_at)
    ).first()

    shelves = ShelfStatus.query.all()

    devices = Device.query.all()

    online = len([
        d for d in devices
        if d.status == "online"
    ])

    offline = len([
        d for d in devices
        if d.status == "offline"
    ])

    return {

        "online_devices": online,

        "offline_devices": offline,

        "latest_camera_event":
            latest_event.to_dict()
            if latest_event else None,

        "latest_footfall":
            latest_footfall.to_dict()
            if latest_footfall else None,

        "total_shelves": len(shelves),

        "low_stock_shelves": len([
            s for s in shelves
            if s.status == "low"
        ]),

        "empty_shelves": len([
            s for s in shelves
            if s.status == "empty"
        ])
    }


# ==========================================================
# DASHBOARD HELPERS
# ==========================================================

def get_queue_status():

    event = CameraEvent.query.filter_by(
        event_type="queue_detected"
    ).order_by(
        desc(CameraEvent.created_at)
    ).first()

    if not event:
        return {
            "queue_length": 0
        }

    return {
        "queue_length":
        event.details.get(
            "queue_length",
            0
        )
    }


def get_people_count():

    event = CameraEvent.query.filter_by(
        event_type="person_detected"
    ).order_by(
        desc(CameraEvent.created_at)
    ).first()

    if not event:
        return {
            "people": 0
        }

    return {
        "people":
        event.details.get(
            "count",
            0
        )
    }


def get_shelf_summary():

    shelves = ShelfStatus.query.all()

    return {

        "total": len(shelves),

        "normal": len([
            s for s in shelves
            if s.status == "normal"
        ]),

        "low": len([
            s for s in shelves
            if s.status == "low"
        ]),

        "empty": len([
            s for s in shelves
            if s.status == "empty"
        ])
    }