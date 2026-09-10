import os
import importlib.util

from .helpers import (
    generate_uuid,
    format_datetime,
    parse_datetime,
    calculate_percentage,
    safe_float,
    safe_int,
)
from .validators import (
    validate_required_fields,
    validate_email,
    validate_numeric_range,
    validate_enum,
)
from .constants import (
    DeviceType,
    DeviceStatus,
    SensorType,
    AlertSeverity,
    AlertCategory,
    ShelfStockStatus,
    UserRole,
    PaymentMethod,
)
from .logger import logger, get_logger
from .response import success_response, error_response, paginated_response

# Backward compatibility: re-export generate_bill_pdf & BorderCanvas from original app/utils.py
try:
    _utils_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "utils.py")
    if os.path.exists(_utils_file):
        _spec = importlib.util.spec_from_file_location("_legacy_utils", _utils_file)
        _mod = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_mod)
        generate_bill_pdf = getattr(_mod, "generate_bill_pdf", None)
        BorderCanvas = getattr(_mod, "BorderCanvas", None)
    else:
        generate_bill_pdf = None
        BorderCanvas = None
except Exception:
    generate_bill_pdf = None
    BorderCanvas = None

__all__ = [
    "generate_uuid",
    "format_datetime",
    "parse_datetime",
    "calculate_percentage",
    "safe_float",
    "safe_int",
    "validate_required_fields",
    "validate_email",
    "validate_numeric_range",
    "validate_enum",
    "DeviceType",
    "DeviceStatus",
    "SensorType",
    "AlertSeverity",
    "AlertCategory",
    "ShelfStockStatus",
    "UserRole",
    "PaymentMethod",
    "logger",
    "get_logger",
    "success_response",
    "error_response",
    "paginated_response",
    "generate_bill_pdf",
    "BorderCanvas",
]

