from app.db import db
from datetime import datetime

class Bill(db.Model):
    __tablename__ = "bills"

    id = db.Column(db.Integer, primary_key=True)

    # Financials
    subtotal = db.Column(db.Float, nullable=False)
    tax_amount = db.Column(db.Float, default=0)
    discount = db.Column(db.Float, default=0)
    total_amount = db.Column(db.Float, nullable=False)

    # Payment
    payment_method = db.Column(db.String(50))  # cash / upi / card

    # Customer (optional but impressive 🔥)
    customer_name = db.Column(db.String(150))
    customer_phone = db.Column(db.String(20))

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship("BillItem", back_populates="bill")