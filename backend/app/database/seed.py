from datetime import datetime, timedelta, date
from werkzeug.security import generate_password_hash
from app.db import db
from app.models import (
    User,
    Product,
    Device,
    ShelfStatus,
    SensorReading,
    CameraEvent,
    Footfall,
    Alert,
)

def seed_database():
    """
    Seeds initial realistic retail & IoT data into the database.
    """
    print("🌱 Starting database seeding...")

    # 1. Seed Users
    if not User.query.filter_by(email="owner@bizmate.com").first():
        owner = User(
            name="Kirana Store Owner",
            email="owner@bizmate.com",
            password=generate_password_hash("admin123"),
            role="owner",
            created_at=datetime.utcnow()
        )
        db.session.add(owner)
        print("  ✓ Added owner user (owner@bizmate.com)")

    if not User.query.filter_by(email="cashier@bizmate.com").first():
        cashier = User(
            name="Counter Cashier",
            email="cashier@bizmate.com",
            password=generate_password_hash("cashier123"),
            role="cashier",
            created_at=datetime.utcnow()
        )
        db.session.add(cashier)
        print("  ✓ Added cashier user (cashier@bizmate.com)")

    # 2. Seed Products
    sample_products = [
        {"name": "Aashirvaad Shudh Chakki Atta 5kg", "category": "Staples", "brand": "ITC", "cost_price": 210.0, "selling_price": 245.0, "quantity": 35, "min_stock_level": 8, "expiry_date": date.today() + timedelta(days=120), "batch_number": "BAT-ITC-2026"},
        {"name": "Fortune Sunlite Sunflower Oil 1L", "category": "Cooking Oils", "brand": "Fortune", "cost_price": 125.0, "selling_price": 145.0, "quantity": 28, "min_stock_level": 6, "expiry_date": date.today() + timedelta(days=180), "batch_number": "BAT-FOR-881"},
        {"name": "Tata Salt Iodized 1kg", "category": "Staples", "brand": "Tata", "cost_price": 22.0, "selling_price": 28.0, "quantity": 50, "min_stock_level": 10, "expiry_date": date.today() + timedelta(days=365), "batch_number": "BAT-TAT-012"},
        {"name": "India Gate Basmati Rice Feast 1kg", "category": "Staples", "brand": "India Gate", "cost_price": 110.0, "selling_price": 135.0, "quantity": 4, "min_stock_level": 8, "expiry_date": date.today() + timedelta(days=90), "batch_number": "BAT-IG-992"},
        {"name": "Amul Taaza Toned Milk 1L", "category": "Dairy", "brand": "Amul", "cost_price": 50.0, "selling_price": 54.0, "quantity": 3, "min_stock_level": 10, "expiry_date": date.today() + timedelta(days=2), "batch_number": "BAT-AML-102"},
        {"name": "Nescafe Classic Coffee 50g", "category": "Beverages", "brand": "Nestle", "cost_price": 165.0, "selling_price": 190.0, "quantity": 22, "min_stock_level": 5, "expiry_date": date.today() + timedelta(days=240), "batch_number": "BAT-NES-331"},
        {"name": "Tata Tea Gold 500g", "category": "Beverages", "brand": "Tata", "cost_price": 240.0, "selling_price": 275.0, "quantity": 18, "min_stock_level": 5, "expiry_date": date.today() + timedelta(days=210), "batch_number": "BAT-TTG-450"},
        {"name": "Lay's India's Magic Masala 50g", "category": "Snacks", "brand": "Lays", "cost_price": 16.0, "selling_price": 20.0, "quantity": 40, "min_stock_level": 12, "expiry_date": date.today() + timedelta(days=60), "batch_number": "BAT-LAY-551"},
        {"name": "Parle-G Gold Biscuits 1kg", "category": "Snacks", "brand": "Parle", "cost_price": 95.0, "selling_price": 110.0, "quantity": 15, "min_stock_level": 6, "expiry_date": date.today() + timedelta(days=150), "batch_number": "BAT-PAR-721"},
        {"name": "Dettol Original Soap 125g", "category": "Personal Care", "brand": "Dettol", "cost_price": 42.0, "selling_price": 50.0, "quantity": 25, "min_stock_level": 8, "expiry_date": date.today() + timedelta(days=300), "batch_number": "BAT-DET-091"},
    ]

    for p_data in sample_products:
        if not Product.query.filter_by(name=p_data["name"]).first():
            product = Product(**p_data)
            db.session.add(product)

    db.session.commit()
    print("  ✓ Verified sample products in database")

    # 3. Seed IoT Devices
    sample_devices = [
        {"device_id": "CAM-ENTRANCE-01", "name": "Entrance High-Res Camera", "device_type": "camera", "location": "Main Entrance", "ip_address": "192.168.1.101", "mac_address": "B8:27:EB:11:22:33", "status": "online"},
        {"device_id": "CAM-BILLING-02", "name": "Billing Counter Camera", "device_type": "camera", "location": "Cash Desk", "ip_address": "192.168.1.102", "mac_address": "B8:27:EB:11:22:34", "status": "online"},
        {"device_id": "HUB-SHELF-A1", "name": "Aisle 1 Weight & IR Hub", "device_type": "sensor_hub", "location": "Aisle 1 Staples", "ip_address": "192.168.1.110", "mac_address": "EC:94:CB:33:44:55", "status": "online"},
        {"device_id": "HUB-COOLER-B1", "name": "Dairy Refrigerator Telemetry", "device_type": "sensor_hub", "location": "Dairy Chiller", "ip_address": "192.168.1.111", "mac_address": "EC:94:CB:33:44:56", "status": "online"},
        {"device_id": "GATE-PIR-01", "name": "Entrance Bidirectional Counter", "device_type": "footfall_counter", "location": "Store Front Gate", "ip_address": "192.168.1.120", "mac_address": "AA:BB:CC:DD:EE:01", "status": "online"},
        {"device_id": "EDGE-AI-JETSON-01", "name": "Store Edge AI Accelerator", "device_type": "edge_ai_box", "location": "Server Rack", "ip_address": "192.168.1.50", "mac_address": "AA:BB:CC:DD:EE:99", "status": "online"},
    ]

    for d_data in sample_devices:
        if not Device.query.filter_by(device_id=d_data["device_id"]).first():
            dev = Device(**d_data, last_heartbeat=datetime.utcnow())
            db.session.add(dev)

    db.session.commit()
    print("  ✓ Verified IoT devices")

    # 4. Seed Smart Shelf Statuses
    atta_prod = Product.query.filter(Product.name.like("%Atta%")).first()
    milk_prod = Product.query.filter(Product.name.like("%Milk%")).first()
    lays_prod = Product.query.filter(Product.name.like("%Lay's%")).first()
    hub_a1 = Device.query.filter_by(device_id="HUB-SHELF-A1").first()
    hub_cooler = Device.query.filter_by(device_id="HUB-COOLER-B1").first()

    sample_shelves = [
        {"shelf_code": "SHELF-A1", "section": "Staples", "product_id": atta_prod.id if atta_prod else None, "device_id": hub_a1.id if hub_a1 else None, "current_stock_estimate": 35, "capacity": 40, "fill_percentage": 87.5, "status": "normal"},
        {"shelf_code": "FRIDGE-B1", "section": "Dairy", "product_id": milk_prod.id if milk_prod else None, "device_id": hub_cooler.id if hub_cooler else None, "current_stock_estimate": 3, "capacity": 25, "fill_percentage": 12.0, "status": "low_stock"},
        {"shelf_code": "SHELF-C1", "section": "Snacks", "product_id": lays_prod.id if lays_prod else None, "device_id": None, "current_stock_estimate": 40, "capacity": 50, "fill_percentage": 80.0, "status": "normal"},
    ]

    for s_data in sample_shelves:
        if not ShelfStatus.query.filter_by(shelf_code=s_data["shelf_code"]).first():
            shelf = ShelfStatus(**s_data, last_checked=datetime.utcnow())
            db.session.add(shelf)

    db.session.commit()
    print("  ✓ Verified Smart Shelves")

    # 5. Seed Sensor Readings
    sample_readings = [
        {"sensor_id_str": "TEMP-CHILLER-01", "sensor_type": "temperature", "value": 3.8, "unit": "°C", "location": "Dairy Chiller", "threshold_min": 2.0, "threshold_max": 6.0, "is_anomaly": False},
        {"sensor_id_str": "TEMP-STORE-01", "sensor_type": "temperature", "value": 24.2, "unit": "°C", "location": "Main Store Floor", "threshold_min": 18.0, "threshold_max": 32.0, "is_anomaly": False},
        {"sensor_id_str": "HUM-STORE-01", "sensor_type": "humidity", "value": 52.0, "unit": "%", "location": "Main Store Floor", "threshold_min": 30.0, "threshold_max": 75.0, "is_anomaly": False},
        {"sensor_id_str": "LOAD-SHELF-A1", "sensor_type": "weight", "value": 175.0, "unit": "kg", "location": "Aisle 1 Staples", "threshold_min": 10.0, "threshold_max": 300.0, "is_anomaly": False},
    ]

    for r_data in sample_readings:
        sr = SensorReading(**r_data, timestamp=datetime.utcnow())
        db.session.add(sr)

    # 6. Seed Camera Events
    cam1 = Device.query.filter_by(device_id="CAM-ENTRANCE-01").first()
    c_events = [
        {"device_id": cam1.id if cam1 else None, "camera_id_str": "CAM-ENTRANCE-01", "event_type": "person_detected", "confidence": 0.98, "details": {"direction": "entry", "zone": "entrance"}, "timestamp": datetime.utcnow() - timedelta(minutes=5)},
        {"device_id": cam1.id if cam1 else None, "camera_id_str": "CAM-ENTRANCE-01", "event_type": "dwell_time_high", "confidence": 0.92, "details": {"dwell_seconds": 180, "zone": "promotional_display"}, "timestamp": datetime.utcnow() - timedelta(minutes=15)},
    ]
    for ce in c_events:
        db.session.add(CameraEvent(**ce))

    # 7. Seed Footfall Data
    now = datetime.utcnow()
    for h in range(8, 20):
        entry_cnt = 12 if 10 <= h <= 13 or 17 <= h <= 19 else 5
        exit_cnt = entry_cnt - (1 if h < 18 else -1)
        db.session.add(Footfall(
            area_name="Main Entrance",
            entry_count=entry_cnt,
            exit_count=max(0, exit_cnt),
            current_occupancy=max(2, entry_cnt - exit_cnt + 3),
            dwell_time_avg_seconds=125.0,
            hourly_bucket=now.strftime(f"%Y-%m-%d {h:02d}:00"),
            timestamp=now.replace(hour=h, minute=0, second=0)
        ))

    # 8. Seed Alerts
    sample_alerts = [
        {"title": "Low Stock Warning: Amul Taaza Milk", "message": "Only 3 packets left on shelf FRIDGE-B1. Minimum threshold is 10.", "severity": "warning", "category": "shelf_stock", "is_read": False, "is_resolved": False},
        {"title": "System Online", "message": "Store Edge AI Box and 6 IoT devices connected successfully.", "severity": "info", "category": "system", "is_read": True, "is_resolved": True},
    ]
    for a_data in sample_alerts:
        if not Alert.query.filter_by(title=a_data["title"]).first():
            db.session.add(Alert(**a_data, created_at=datetime.utcnow()))

    db.session.commit()
    print("✅ Database seeding completed successfully!")


if __name__ == "__main__":
    import sys
    import os
    # Ensure backend path is on sys.path
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)

    from app import create_app
    app = create_app()
    with app.app_context():
        seed_database()

