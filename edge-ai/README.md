# BIZmate Edge-AI Module

Real-time computer vision and sensor processing system for retail store monitoring. Runs on edge devices (Raspberry Pi, Jetson, or Linux PCs) to detect people, queue lengths, shelf stock levels, and collect sensor telemetry.

## Features

- **Computer Vision**: YOLO-based person detection, queue monitoring, and shelf stock analysis
- **Sensor Integration**: Temperature, humidity, weight (load cell), ultrasonic distance, and IR footfall sensors
- **Real-time Processing**: Frame-by-frame analysis with configurable inference rates
- **Backend Integration**: REST API communication with BIZmate Flask backend
- **Hardware Support**: Real GPIO sensors on Raspberry Pi, mock mode for testing
- **Offline Buffering**: Events cached when backend is unreachable

## System Requirements

- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended)
- 10GB free disk space
- Camera: USB webcam, IP camera, or Android smartphone with IP Webcam app
- Optional: Raspberry Pi 4+ or Jetson Nano for hardware sensor support

## Installation

### 1. Clone and Navigate

```bash
cd edge-ai/
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the `edge-ai/` directory:

```env
# Backend Configuration
BACKEND_API_URL=http://127.0.0.1:5000
BACKEND_API_KEY=

# Device Identification
DEVICE_ID=edge-ai-device-001
DEVICE_NAME=Edge AI Box
DEVICE_TYPE=edge_ai_box
DEVICE_LOCATION=Store Floor
IP_ADDRESS=
MAC_ADDRESS=
FIRMWARE_VERSION=1.0.0

# Camera Configuration
CAMERA_SOURCE=0
CAMERA_FPS=30
CAMERA_WIDTH=1280
CAMERA_HEIGHT=720
CAMERA_WARMUP_FRAMES=30
ENABLE_FRAME_PREVIEW=false

# AI Model Configuration
YOLO_MODEL_NAME=yolo11n.pt
YOLO_WEIGHTS_PATH=weights/yolov11.pt
MODEL_CONFIDENCE_THRESHOLD=0.5
MODEL_IOU_THRESHOLD=0.45
INFERENCE_SKIP_FRAMES=3
ENABLE_GPU=false

# Sensor Configuration
ENABLE_DHT22=false
DHT22_PIN=17
ENABLE_HX711=false
HX711_DATA_PIN=5
HX711_CLOCK_PIN=6
ENABLE_PIR=false
PIR_PIN=27
ENABLE_ULTRASONIC=false
ULTRASONIC_TRIG_PIN=23
ULTRASONIC_ECHO_PIN=24
USE_MOCK_SENSORS=true
SENSOR_READ_INTERVAL_SECONDS=30

# Communication Configuration
HEARTBEAT_INTERVAL_SECONDS=60
REQUEST_TIMEOUT_SECONDS=10
RECONNECT_RETRY_ATTEMPTS=3
RECONNECT_BACKOFF_SECONDS=5
EVENT_BATCH_SIZE=10
EVENT_FLUSH_INTERVAL_SECONDS=5

# Logging & Debug
LOG_LEVEL=INFO
LOG_FILE=logs/edge_ai.log
DEBUG_MODE=false
SAVE_DETECTION_SNAPSHOTS=false
SNAPSHOT_DIR=snapshots/

# Detection Thresholds
PERSON_COUNT_WARNING=5
QUEUE_LENGTH_THRESHOLD=3
DWELL_TIME_WARNING_SECONDS=30
```

## Camera Setup

### USB Webcam

For a USB webcam, set in `.env`:

```env
CAMERA_SOURCE=0  # Use 0 for default camera, 1 for second, etc.
```

### IP Camera

For RTSP IP cameras:

```env
CAMERA_SOURCE=rtsp://192.168.1.100:554/stream
```

### Android IP Webcam

Use your Android smartphone as a camera:

1. Install [IP Webcam](https://play.google.com/store/apps/details?id=com.pas.webcam) app
2. Open the app and start the server
3. Note your phone's IP address (shown in the app)
4. Configure in `.env`:

```env
CAMERA_SOURCE=http://192.168.1.XX:8080/video
```

Replace `192.168.1.XX` with your phone's actual IP address.

## Running the Application

### Start the Edge AI Daemon

```bash
python app.py
```

The command must be run from `edge-ai/` after installing `requirements.txt`. It validates configuration first and exits with a clear error if OpenCV, the YOLO runtime, the backend, or the configured camera is unavailable.

The daemon will:
1. Validate configuration
2. Register device with backend
3. Initialize camera and load YOLO model
4. Start detection loop (people, queue, shelf)
5. Send events and sensor readings to backend
6. Send periodic heartbeats

### Stop the Daemon

Press `Ctrl+C` for graceful shutdown.

## Directory Structure

```
edge-ai/
├── app.py                      # Main application daemon
├── config.py                   # Configuration management
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create this)
├── .env.example               # Environment variables template
├── README.md                  # This file
│
├── ai/                        # Computer Vision Modules
│   ├── __init__.py
│   ├── model_loader.py        # YOLO model loading
│   ├── inference.py           # Inference engine
│   ├── people_detector.py     # Person detection & tracking
│   ├── queue_detector.py      # Queue length analysis
│   ├── shelf_detector.py      # Shelf stock monitoring
│   └── tracker.py             # Object tracking
│
├── camera/                    # Camera Handling
│   ├── __init__.py
│   ├── mobile_camera.py       # Camera stream management
│   ├── stream_handler.py      # Frame buffering
│   ├── frame_processor.py     # Frame processing
│   └── reconnect.py           # Reconnection logic
│
├── sensors/                   # Sensor Management
│   ├── __init__.py
│   ├── sensor_manager.py      # Central sensor coordinator
│   ├── ir_sensor.py           # IR footfall sensor
│   ├── ultrasonic_sensor.py   # Ultrasonic distance sensor
│   ├── mock_sensor.py         # Mock sensor simulator
│   └── sensor_sender.py       # Sensor data transmission
│
├── events/                    # Event System
│   ├── __init__.py
│   ├── event_builder.py       # Event construction
│   ├── event_sender.py        # Event queuing & transmission
│   └── event_types.py         # Event data structures
│
├── communication/             # Backend Communication
│   ├── __init__.py
│   ├── backend_client.py      # REST API client
│   └── websocket_client.py    # WebSocket client (optional)
│
├── utils/                     # Utilities
│   ├── __init__.py
│   ├── logger.py              # Logging system
│   ├── helpers.py             # Helper functions
│   ├── constants.py           # Constants & enums
│   └── image_utils.py         # Image processing utilities
│
├── weights/                   # Model Weights
│   ├── yolov11.pt             # YOLO model (downloaded on first run)
│   └── coco.names             # COCO class names
│
├── tests/                     # Unit Tests
│   ├── test_config.py
│   ├── test_detectors.py
│   ├── test_sensors.py
│   └── test_events.py
│
├── logs/                      # Runtime Logs (auto-created)
└── snapshots/                 # Detection Snapshots (auto-created)
```

## Configuration

### Queue Detection

Configure the billing counter ROI and threshold:

```env
# In .env
QUEUE_LENGTH_THRESHOLD=3  # Alert when queue >= 3 people
```

Or set programmatically in `app.py`:

```python
queue_roi = [100, 300, 400, 200]  # [x, y, width, height]
queue_detector.set_roi(queue_roi)
```

### Shelf Monitoring

Configure shelf regions in `app.py`:

```python
from ai.shelf_detector import ShelfConfig

shelf_configs = [
    ShelfConfig(
        shelf_id="A1",
        roi=[50, 200, 300, 150],
        product_classes=[39, 41],  # bottle, cup
        expected_capacity=12,
        low_stock_threshold=30.0,
        empty_threshold=10.0,
    ),
]
```

### Sensor Thresholds

Adjust sensor anomaly thresholds in `utils/constants.py`:

```python
class SensorThresholds:
    TEMPERATURE_MIN = 15.0
    TEMPERATURE_MAX = 28.0
    HUMIDITY_MIN = 30.0
    HUMIDITY_MAX = 70.0
    # ... etc
```

## Hardware Setup (Raspberry Pi)

### GPIO Pin Configuration

Default GPIO pins (configurable in `.env`):

- DHT22 (Temperature/Humidity): GPIO 17
- HX711 (Load Cell): DATA GPIO 5, CLOCK GPIO 6
- PIR (Motion/IR): GPIO 27
- Ultrasonic HC-SR04: TRIG GPIO 23, ECHO GPIO 24

### Install Hardware Libraries

```bash
# GPIO control
pip install RPi.GPIO

# DHT22 sensor
pip install Adafruit-DHT

# HX711 load cell
pip install hx711
```

### Wiring Reference

- **DHT22**: VCC → 3.3V, GND → GND, DATA → GPIO 17
- **HX711**: VCC → 3.3V, GND → GND, DATA → GPIO 5, CLOCK → GPIO 6
- **PIR**: VCC → 5V, GND → GND, OUT → GPIO 27
- **HC-SR04**: VCC → 5V, GND → GND, TRIG → GPIO 23, ECHO → GPIO 24

## Troubleshooting

### Camera Not Starting

- Check `CAMERA_SOURCE` in `.env`
- For USB webcams, try different indices (0, 1, 2)
- For IP cameras, verify network connectivity and URL format
- Check camera permissions on Linux: `sudo usermod -a -G video $USER`

### Model Not Loading

- First run will download YOLO model automatically
- Check internet connection for initial download
- Verify `weights/` directory is writable
- For manual download, place `yolov11.pt` in `weights/` directory

### Backend Connection Failed

- Verify `BACKEND_API_URL` in `.env`
- Check backend is running: `curl http://127.0.0.1:5000/`
- Check firewall settings
- Review logs in `logs/edge_ai.log`

### High CPU Usage

- Increase `INFERENCE_SKIP_FRAMES` to run inference less frequently
- Reduce `CAMERA_FPS` and resolution
- Use smaller YOLO model: `YOLO_MODEL_NAME=yolo11n.pt`
- Enable GPU if available: `ENABLE_GPU=true`

### Sensor Readings Failing

- Enable mock mode for testing: `USE_MOCK_SENSORS=true`
- Check GPIO pin assignments in `.env`
- Verify hardware connections with multimeter
- Check sensor-specific logs in `logs/edge_ai.log`

## Testing

Run the test suite:

```bash
pytest tests/
```

Run specific test files:

```bash
pytest tests/test_config.py
pytest tests/test_detectors.py
pytest tests/test_sensors.py
pytest tests/test_events.py
```

## Development

### Adding New Detectors

1. Create detector class in `ai/`
2. Inherit from base patterns in `people_detector.py`
3. Add to main loop in `app.py`
4. Register events in `event_builder.py`

### Adding New Sensors

1. Create sensor reader in `sensors/`
2. Add to `SensorManager` in `sensor_manager.py`
3. Add sensor type to `SensorType` in `utils/constants.py`
4. Update event builder if needed

## Performance Optimization

### Frame Skip Configuration

Adjust inference frequency:

```env
INFERENCE_SKIP_FRAMES=3  # Run inference every 3rd frame
```

Higher values = lower CPU usage, slower detection response.

### Model Selection

Available YOLO models (speed vs accuracy):

- `yolo11n.pt` - Fastest, lowest accuracy (recommended for edge)
- `yolo11s.pt` - Balanced
- `yolo11m.pt` - Slower, higher accuracy
- `yolo11l.pt` - Slowest, highest accuracy

### GPU Acceleration

Enable CUDA GPU if available:

```env
ENABLE_GPU=true
```

Requires PyTorch with CUDA support.

## Security

- Never commit `.env` file with real API keys
- Use `BACKEND_API_KEY` for authentication
- Keep firmware updated
- Use HTTPS for backend URLs in production
- Restrict network access to trusted IPs

## License

Part of BIZmate project. See main project LICENSE file.

## Support

For issues and questions:
- Check logs in `logs/edge_ai.log`
- Review configuration in `.env`
- Consult main project documentation
- Contact development team
