import re

def validate_required_fields(data, required_fields):
    if not isinstance(data, dict):
        return False, "Request body must be a valid JSON object"
    missing = [field for field in required_fields if field not in data or data[field] is None or (isinstance(data[field], str) and data[field].strip() == "")]
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"
    return True, None


def validate_email(email):
    if not email or not isinstance(email, str):
        return False
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email.strip()) is not None


def validate_numeric_range(val, min_val=None, max_val=None, field_name="value"):
    try:
        num = float(val)
    except (ValueError, TypeError):
        return False, f"{field_name} must be a number"
    if min_val is not None and num < min_val:
        return False, f"{field_name} cannot be less than {min_val}"
    if max_val is not None and num > max_val:
        return False, f"{field_name} cannot be greater than {max_val}"
    return True, None


def validate_enum(val, allowed_values, field_name="field"):
    if val not in allowed_values:
        return False, f"Invalid {field_name}: '{val}'. Allowed values: {', '.join(str(v) for v in allowed_values)}"
    return True, None

