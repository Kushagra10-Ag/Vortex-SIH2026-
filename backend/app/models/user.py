from app.db import db
from datetime import datetime
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(50), default="owner")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)