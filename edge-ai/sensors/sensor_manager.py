from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/receive', methods=['POST'])
def receive_data():
    data = request.get_json(silent=True)
    
    if not data:
        return jsonify({"status": "error", "message": "Invalid JSON"}), 400

    distance = data.get("distance_cm")
    ir_status = data.get("ir_obstacle")

    print(f"\n[INCOMING WEBHOOK]")
    print(f"Distance: {distance} cm | IR Detected: {ir_status}")
    print(f"Raw Payload: {data}")

    return jsonify({"status": "success", "received": data}), 200

if __name__ == '__main__':
    # host='0.0.0.0' binds to all network interfaces
    app.run(host='0.0.0.0', port=5005, debug=True)