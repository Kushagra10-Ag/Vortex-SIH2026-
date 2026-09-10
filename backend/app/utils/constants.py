"""
Constants and Enums for BIZmate Retail & Edge Architecture
"""

class DeviceType:
    CAMERA = "camera"
    SENSOR_HUB = "sensor_hub"
    FOOTFALL_COUNTER = "footfall_counter"
    EDGE_AI_BOX = "edge_ai_box"
    GATEWAY = "gateway"

    ALL = [CAMERA, SENSOR_HUB, FOOTFALL_COUNTER, EDGE_AI_BOX, GATEWAY]


class DeviceStatus:
    ONLINE = "online"
    OFFLINE = "offline"
    WARNING = "warning"
    MAINTENANCE = "maintenance"

    ALL = [ONLINE, OFFLINE, WARNING, MAINTENANCE]


class SensorType:
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    WEIGHT = "weight"
    IR_DISTANCE = "ir_distance"
    MOTION_PIR = "motion_pir"
    AMBIENT_LIGHT = "ambient_light"

    ALL = [TEMPERATURE, HUMIDITY, WEIGHT, IR_DISTANCE, MOTION_PIR, AMBIENT_LIGHT]


class AlertSeverity:
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

    ALL = [INFO, WARNING, CRITICAL]


class AlertCategory:
    SHELF_STOCK = "shelf_stock"
    THEFT_SECURITY = "theft_security"
    SENSOR_ANOMALY = "sensor_anomaly"
    DEVICE_OFFLINE = "device_offline"
    EXPIRY_WARNING = "expiry_warning"
    FOOTFALL_SURGE = "footfall_surge"
    SYSTEM = "system"

    ALL = [
        SHELF_STOCK,
        THEFT_SECURITY,
        SENSOR_ANOMALY,
        DEVICE_OFFLINE,
        EXPIRY_WARNING,
        FOOTFALL_SURGE,
        SYSTEM,
    ]


class ShelfStockStatus:
    NORMAL = "normal"
    LOW_STOCK = "low_stock"
    EMPTY = "empty"
    MISPLACED_ITEM = "misplaced_item"

    ALL = [NORMAL, LOW_STOCK, EMPTY, MISPLACED_ITEM]


class UserRole:
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    CASHIER = "cashier"

    ALL = [OWNER, ADMIN, MANAGER, CASHIER]


class PaymentMethod:
    CASH = "cash"
    UPI = "upi"
    CARD = "card"

    ALL = [CASH, UPI, CARD]

