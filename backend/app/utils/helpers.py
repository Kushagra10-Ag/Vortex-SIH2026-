from datetime import datetime, timezone
import uuid

def generate_uuid(prefix=""):
    uid = uuid.uuid4().hex[:12]
    return f"{prefix}_{uid}" if prefix else uid


def format_datetime(dt, fmt="%Y-%m-%d %H:%M:%S"):
    if not dt:
        return ""
    if isinstance(dt, str):
        return dt
    return dt.strftime(fmt)


def parse_datetime(dt_str):
    if not dt_str:
        return datetime.utcnow()
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return datetime.utcnow()


def calculate_percentage(part, total):
    if not total or total <= 0:
        return 0.0
    return round((part / total) * 100.0, 2)


def safe_float(value, default=0.0):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int(value, default=0):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

