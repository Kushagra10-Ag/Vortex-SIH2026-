from app.db import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)

    # Basic Info
    name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(100), index=True)
    brand = db.Column(db.String(100))

    # Pricing
    cost_price = db.Column(db.Float, nullable=False)
    selling_price = db.Column(db.Float, nullable=False)

    # Inventory
    quantity = db.Column(db.Integer, nullable=False)
    min_stock_level = db.Column(db.Integer, default=5)

    # Expiry & batch
    expiry_date = db.Column(db.Date)
    batch_number = db.Column(db.String(100))  # 🔥 new (real-world)

    # Status
    is_active = db.Column(db.Boolean, default=True)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    bill_items = db.relationship("BillItem", back_populates="product")