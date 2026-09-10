from app.db import db
from datetime import datetime

class ShelfStatus(db.Model):
    __tablename__ = "shelf_statuses"

    id = db.Column(db.Integer, primary_key=True)
    shelf_code = db.Column(db.String(100), unique=True, nullable=False, index=True)
    section = db.Column(db.String(100), default="General", index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=True, index=True)
    device_id = db.Column(db.Integer, db.ForeignKey("devices.id"), nullable=True, index=True)

    current_stock_estimate = db.Column(db.Integer, default=0)
    capacity = db.Column(db.Integer, default=50)
    fill_percentage = db.Column(db.Float, default=100.0)
    status = db.Column(db.String(50), default="normal", index=True)  # normal, low_stock, empty, misplaced_item

    last_checked = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    product = db.relationship("Product", foreign_keys=[product_id])
    device = db.relationship("Device", back_populates="shelf_statuses")

    def to_dict(self):
        return {
            "id": self.id,
            "shelf_code": self.shelf_code,
            "section": self.section,
            "product_id": self.product_id,
            "product_name": self.product.name if self.product else None,
            "device_id": self.device_id,
            "current_stock_estimate": self.current_stock_estimate,
            "capacity": self.capacity,
            "fill_percentage": round(float(self.fill_percentage or 0.0), 1),
            "status": self.status,
            "last_checked": self.last_checked.isoformat() if self.last_checked else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

