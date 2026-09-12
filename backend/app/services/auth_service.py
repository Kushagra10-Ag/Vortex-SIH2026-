from app.models import User
from app.db import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from datetime import datetime, timedelta, timezone
import jwt

def register_user(data):
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "owner")

    if not email or not password:
        return {"error": "Email and password are required"}, 400

    existing_user = User.query.filter_by(email=email.strip().lower()).first()
    if existing_user:
        return {"error": "User already exists"}, 400

    user = User(
        name=name.strip() if name else "",
        email=email.strip().lower(),
        password=generate_password_hash(password),
        role=role
    )

    db.session.add(user)
    db.session.commit()

    token = create_jwt_token(user)

    return {
        "message": "User registered successfully",
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
        }
    }, 201


def authenticate_user(data):
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return {"error": "Email and password are required"}, 400

    user = User.query.filter_by(email=email.strip().lower()).first()
    if not user or not check_password_hash(user.password, password):
        return {"error": "Invalid email or password"}, 401

    token = create_jwt_token(user)

    return {
        "message": "Login successful",
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": getattr(user, "role", "owner"),
        }
    }, 200


def create_jwt_token(user, expires_in_days=7):
    secret_key = current_app.config.get("JWT_SECRET_KEY") or current_app.config.get("SECRET_KEY")
    if not secret_key:
        raise RuntimeError("JWT secret is not configured")
    payload = {
        "sub": user.id,
        "user_id": user.id,
        "email": user.email,
        "role": getattr(user, "role", "owner"),
        "exp": datetime.now(timezone.utc) + timedelta(days=expires_in_days),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, secret_key, algorithm="HS256")


def get_user_by_id(user_id):
    user = User.query.get(user_id)
    if not user:
        return None
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": getattr(user, "role", "owner"),
    }

