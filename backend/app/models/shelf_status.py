from app.db import db
from datetime import datetime


class ShelfStatus(db.Model):
    __tablename__ = "shelf_statuses"

    id = db.Column(db.Integer, primary_key=True)

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id")
    )

    device_id = db.Column(
        db.Integer,
        db.ForeignKey("devices.id")
    )

    estimated_quantity = db.Column(
        db.Integer,
        default=0
    )

    confidence = db.Column(
        db.Float,
        default=1.0
    )

    status = db.Column(
        db.String(30),
        default="normal"
    )
    # normal
    # low
    # empty

    last_checked = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    product = db.relationship(
    "Product",
    back_populates="shelf_statuses"
)

    device = db.relationship(
        "Device",
        back_populates="shelf_statuses"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "product_name": self.product.name if self.product else None,
            "device_id": self.device.device_id if self.device else self.device_id,
            "estimated_quantity": self.estimated_quantity,
            "confidence": self.confidence,
            "status": self.status,
            "last_checked": self.last_checked.isoformat() if self.last_checked else None,
        }