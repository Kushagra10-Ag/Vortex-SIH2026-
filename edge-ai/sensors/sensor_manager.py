from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/receive', methods=['POST'])
def receive_data():
    data = request.get_json(silent=True)
    
    if not data:
        return jsonify({"status": "error", "message": "Invalid JSON"}), 400

<<<<<<< HEAD
    distance = data.get("distance_cm")
    ir_status = data.get("ir_obstacle")
=======
from .mock_sensor import MockSensorReader
from .ir_sensor import IRSensorReader
from .ultrasonic_sensor import UltrasonicSensorReader
from utils.constants import SensorThresholds, SensorType
from utils.logger import log_info, log_warning, log_debug, log_error
from config import EdgeAIConfig
>>>>>>> f21e2ceb7d8ee73136924a0820ceadbab67c17d9

    print(f"\n[INCOMING WEBHOOK]")
    print(f"Distance: {distance} cm | IR Detected: {ir_status}")
    print(f"Raw Payload: {data}")

    return jsonify({"status": "success", "received": data}), 200

if __name__ == '__main__':
    # host='0.0.0.0' binds to all network interfaces
    app.run(host='0.0.0.0', port=5000, debug=True)