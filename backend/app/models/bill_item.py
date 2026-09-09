from app.db import db

class BillItem(db.Model):
    __tablename__ = "bill_items"

    id = db.Column(db.Integer, primary_key=True)

    bill_id = db.Column(db.Integer, db.ForeignKey("bills.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)

    # Snapshot (VERY IMPORTANT 🔥)
    product_name = db.Column(db.String(150))
    category = db.Column(db.String(100))

    quantity = db.Column(db.Integer, nullable=False)

    cost_price = db.Column(db.Float)
    selling_price = db.Column(db.Float)

    total_price = db.Column(db.Float)

    bill = db.relationship("Bill", back_populates="items")
    product = db.relationship("Product", back_populates="bill_items")