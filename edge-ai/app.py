"""
Edge-AI Main Application Daemon
Entry point for the edge AI vision and sensor processing system.

Lifecycle:
  1. Validate configuration
  2. Register device with backend
  3. Initialize camera stream
  4. Load YOLO model
  5. Start inference loop: people + queue + shelf detection
  6. Send events via EventSender
  7. Send sensor readings via SensorSender
  8. Send periodic heartbeats
  9. Clean shutdown on SIGINT/SIGTERM
"""

import signal
import sys
import time
import threading
from typing import Optional

import numpy as np

from config import EdgeAIConfig
from ai.model_loader import ModelLoader
from ai.inference import InferenceEngine
from ai.people_detector import PeopleDetector
from ai.queue_detector import QueueDetector
from ai.shelf_detector import ShelfDetector, create_default_shelf_configs
from ai.tracker import CentroidTracker
from camera.mobile_camera import MobileCamera
from events.event_builder import EventBuilder
from events.event_sender import EventSender
from communication.backend_client import BackendClient
from sensors.sensor_manager import SensorManager
from sensors.sensor_sender import SensorSender
from utils.logger import log_info, log_warning, log_error, log_debug


class EdgeAIDaemon:
    """
    Main daemon orchestrating all edge AI components.

    Manages the complete lifecycle from initialization to graceful shutdown.
    """

    def __init__(self):
        self._config = EdgeAIConfig
        self._running = False
        self._shutdown_requested = False

        # Components (initialized in setup())
        self._camera: Optional[MobileCamera] = None
        self._model_loader: Optional[ModelLoader] = None
        self._inference_engine: Optional[InferenceEngine] = None
        self._tracker: Optional[CentroidTracker] = None
        self._people_detector: Optional[PeopleDetector] = None
        self._queue_detector: Optional[QueueDetector] = None
        self._shelf_detector: Optional[ShelfDetector] = None
        self._sensor_manager: Optional[SensorManager] = None
        self._event_builder: Optional[EventBuilder] = None
        self._backend_client: Optional[BackendClient] = None
        self._event_sender: Optional[EventSender] = None
        self._sensor_sender: Optional[SensorSender] = None

        # Thread management
        self._main_thread: Optional[threading.Thread] = None
        self._heartbeat_thread: Optional[threading.Thread] = None

        # Statistics
        self._start_time: float = 0.0
        self._frames_processed = 0

    # ─────────────────────────────────────────────────────────────────────────
    # LIFECYCLE
    # ─────────────────────────────────────────────────────────────────────────

    def setup(self) -> bool:
        """
        Initialize all components and validate configuration.

        Returns:
            True if setup succeeded, False otherwise.
        """
        log_info("[EdgeAIDaemon] Starting setup...")

        # 1. Validate configuration
        is_valid, errors = self._config.validate()
        if not is_valid:
            log_error(f"[EdgeAIDaemon] Configuration validation failed: {errors}")
            return False
        log_info("[EdgeAIDaemon] Configuration validated ✓")

        # 2. Initialize backend client
        self._backend_client = BackendClient()
        log_info("[EdgeAIDaemon] Backend client initialized")

        # 3. Register device with backend
        if not self._register_device():
            log_warning("[EdgeAIDaemon] Device registration failed - will retry on heartbeat")

        # 4. Initialize camera
        if not self._init_camera():
            log_error("[EdgeAIDaemon] Camera initialization failed")
            return False
        log_info("[EdgeAIDaemon] Camera initialized ✓")

        # 5. Load YOLO model
        if not self._load_model():
            log_error("[EdgeAIDaemon] Model loading failed")
            return False
        log_info("[EdgeAIDaemon] YOLO model loaded ✓")

        # 6. Initialize AI detectors
        self._init_detectors()
        log_info("[EdgeAIDaemon] AI detectors initialized ✓")

        # 7. Initialize sensor manager
        self._sensor_manager = SensorManager()
        log_info("[EdgeAIDaemon] Sensor manager initialized ✓")

        # 8. Initialize event builder
        self._event_builder = EventBuilder(
            device_id=self._config.DEVICE_ID,
            capture_snapshots=self._config.SAVE_DETECTION_SNAPSHOTS
        )

        # 9. Initialize event sender
        self._event_sender = EventSender(
            backend_client=self._backend_client,
            batch_size=self._config.EVENT_BATCH_SIZE,
            flush_interval=self._config.EVENT_FLUSH_INTERVAL_SECONDS
        )

        # 10. Initialize sensor sender
        self._sensor_sender = SensorSender(
            sensor_manager=self._sensor_manager,
            event_builder=self._event_builder,
            backend_client=self._backend_client,
            read_interval=self._config.SENSOR_READ_INTERVAL_SECONDS
        )

        log_info("[EdgeAIDaemon] Setup completed successfully ✓")
        return True

    def start(self):
        """Start the main processing loop and background threads."""
        if self._running:
            log_warning("[EdgeAIDaemon] Already running")
            return

        log_info("[EdgeAIDaemon] Starting daemon...")
        self._running = True
        self._start_time = time.time()

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # Start event sender thread
        self._event_sender.start()

        # Start sensor sender thread
        self._sensor_sender.start()

        # Start heartbeat thread
        self._heartbeat_thread = threading.Thread(
            target=self._heartbeat_loop,
            name="heartbeat-loop",
            daemon=True
        )
        self._heartbeat_thread.start()

        # Start main inference loop
        self._main_thread = threading.Thread(
            target=self._main_loop,
            name="inference-loop",
            daemon=False  # Main thread - we'll join it
        )
        self._main_thread.start()

        log_info("[EdgeAIDaemon] Daemon started ✓")

    def run(self):
        """Run the daemon (blocking call)."""
        self.start()
        try:
            # Join main thread - this blocks until shutdown
            self._main_thread.join()
        except KeyboardInterrupt:
            log_info("[EdgeAIDaemon] Keyboard interrupt received")
        finally:
            self.stop()

    def stop(self):
        """Gracefully shutdown all components."""
        if not self._running:
            return

        log_info("[EdgeAIDaemon] Initiating shutdown...")
        self._shutdown_requested = True
        self._running = False

        # Stop threads
        if self._event_sender:
            self._event_sender.stop()
        if self._sensor_sender:
            self._sensor_sender.stop()

        # Cleanup camera
        if self._camera:
            self._camera.release()

        # Cleanup sensors
        if self._sensor_manager:
            self._sensor_manager.cleanup()

        # Print statistics
        self._print_stats()

        log_info("[EdgeAIDaemon] Shutdown complete ✓")

    # ─────────────────────────────────────────────────────────────────────────
    # INITIALIZATION HELPERS
    # ─────────────────────────────────────────────────────────────────────────

    def _register_device(self) -> bool:
        """Register device with backend."""
        try:
            return self._backend_client.register_device()
        except Exception as e:
            log_error(f"[EdgeAIDaemon] Device registration error: {e}")
            return False

    def _init_camera(self) -> bool:
        """Initialize camera stream."""
        try:
            self._camera = MobileCamera(
                source=self._config.CAMERA_SOURCE,
                width=self._config.CAMERA_WIDTH,
                height=self._config.CAMERA_HEIGHT,
                fps=self._config.CAMERA_FPS
            )
            if not self._camera.start():
                log_error("[EdgeAIDaemon] Failed to start camera")
                return False
            return True
        except Exception as e:
            log_error(f"[EdgeAIDaemon] Camera initialization error: {e}")
            return False

    def _load_model(self) -> bool:
        """Load YOLO model."""
        try:
            self._model_loader = ModelLoader()
            model = self._model_loader.load()
            if model is None:
                log_error("[EdgeAIDaemon] Model loading returned None")
                return False

            self._inference_engine = InferenceEngine(
                model_loader=self._model_loader,
                confidence=self._config.MODEL_CONFIDENCE_THRESHOLD,
                iou=self._config.MODEL_IOU_THRESHOLD,
                skip_frames=self._config.INFERENCE_SKIP_FRAMES
            )
            return True
        except Exception as e:
            log_error(f"[EdgeAIDaemon] Model loading error: {e}")
            return False

    def _init_detectors(self):
        """Initialize all AI detectors."""
        # Initialize tracker
        self._tracker = CentroidTracker(
            max_disappeared=30,
            max_distance=100
        )

        # Initialize people detector
        self._people_detector = PeopleDetector(
            inference_engine=self._inference_engine,
            tracker=self._tracker,
            event_builder=self._event_builder,
            person_event_interval_s=5.0,
            dwell_threshold_s=self._config.DWELL_TIME_WARNING_SECONDS
        )

        # Initialize queue detector (with default ROI - can be configured)
        queue_roi = [100, 300, 400, 200]  # Default billing counter ROI
        self._queue_detector = QueueDetector(
            inference_engine=self._inference_engine,
            tracker=self._tracker,
            event_builder=self._event_builder,
            roi=queue_roi,
            queue_threshold=self._config.QUEUE_LENGTH_THRESHOLD,
            service_time_seconds=2.0
        )

        # Initialize shelf detector with default configurations
        shelf_configs = create_default_shelf_configs()
        self._shelf_detector = ShelfDetector(
            inference_engine=self._inference_engine,
            event_builder=self._event_builder,
            shelf_configs=shelf_configs,
            out_of_stock_threshold=10.0  # 10% fill = out of stock
        )

    # ─────────────────────────────────────────────────────────────────────────
    # MAIN PROCESSING LOOP
    # ─────────────────────────────────────────────────────────────────────────

    def _main_loop(self):
        """Main inference loop: capture frame → detect → send events."""
        log_info("[EdgeAIDaemon] Main inference loop started")

        while self._running and not self._shutdown_requested:
            loop_start = time.time()

            try:
                # 1. Capture frame
                frame = self._camera.read()
                if frame is None:
                    log_warning("[EdgeAIDaemon] Failed to read frame - retrying...")
                    time.sleep(0.1)
                    continue

                # 2. Run people detection
                people_events, person_count = self._people_detector.process(frame)

                # 3. Run queue detection
                queue_events, queue_count, wait_time = self._queue_detector.process(frame)

                # 4. Run shelf detection
                shelf_events, shelf_states = self._shelf_detector.process(frame)

                # 5. Enqueue all events
                all_events = people_events + queue_events + shelf_events
                for event in all_events:
                    self._event_sender.enqueue(event)

                # 6. Check IR sensor for footfall
                crossing = self._sensor_manager.read_ir_crossing()
                if crossing:
                    log_debug(f"[EdgeAIDaemon] IR crossing: {crossing}")

                # 7. Update statistics
                self._frames_processed += 1

                # Log status periodically
                if self._frames_processed % 30 == 0:
                    fps = self._frames_processed / (time.time() - self._start_time)
                    log_debug(
                        f"[EdgeAIDaemon] Status: frames={self._frames_processed}, "
                        f"fps={fps:.1f}, people={person_count}, queue={queue_count}, "
                        f"wait={wait_time:.1f}s, events_queued={self._event_sender.queue_size()}"
                    )

            except Exception as e:
                log_error(f"[EdgeAIDaemon] Main loop error: {e}")
                time.sleep(0.5)  # Brief pause on error

            # Control frame rate
            elapsed = time.time() - loop_start
            target_frame_time = 1.0 / self._config.CAMERA_FPS
            sleep_time = max(0, target_frame_time - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)

        log_info("[EdgeAIDaemon] Main inference loop stopped")

    def _heartbeat_loop(self):
        """Send periodic heartbeats to backend."""
        log_info("[EdgeAIDaemon] Heartbeat loop started")

        while self._running and not self._shutdown_requested:
            try:
                time.sleep(self._config.HEARTBEAT_INTERVAL_SECONDS)

                if not self._running:
                    break

                # Build heartbeat event
                uptime = time.time() - self._start_time
                heartbeat = self._event_builder.heartbeat(
                    status="online",
                    uptime_seconds=uptime,
                    firmware_version=self._config.FIRMWARE_VERSION
                )

                # Send heartbeat
                success = self._backend_client.send_heartbeat(heartbeat)
                if success:
                    log_debug("[EdgeAIDaemon] Heartbeat sent successfully")
                else:
                    log_warning("[EdgeAIDaemon] Heartbeat failed - will retry")

            except Exception as e:
                log_error(f"[EdgeAIDaemon] Heartbeat loop error: {e}")

        log_info("[EdgeAIDaemon] Heartbeat loop stopped")

    # ─────────────────────────────────────────────────────────────────────────
    # SIGNAL HANDLING
    # ─────────────────────────────────────────────────────────────────────────

    def _signal_handler(self, signum, frame):
        """Handle SIGINT/SIGTERM for graceful shutdown."""
        log_info(f"[EdgeAIDaemon] Signal {signum} received - initiating shutdown")
        self._shutdown_requested = True

    # ─────────────────────────────────────────────────────────────────────────
    # STATISTICS
    # ─────────────────────────────────────────────────────────────────────────

    def _print_stats(self):
        """Print runtime statistics."""
        if self._start_time == 0:
            return

        uptime = time.time() - self._start_time
        avg_fps = self._frames_processed / uptime if uptime > 0 else 0

        log_info("=" * 50)
        log_info("EDGE-AI DAEMON STATISTICS")
        log_info("=" * 50)
        log_info(f"Uptime: {uptime:.1f} seconds")
        log_info(f"Frames processed: {self._frames_processed}")
        log_info(f"Average FPS: {avg_fps:.2f}")
        log_info(f"Event sender stats: {self._event_sender.stats()}")
        log_info(f"Sensor sender stats: {self._sensor_sender.stats()}")
        log_info("=" * 50)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def main():
    """Main entry point for the edge AI daemon."""
    log_info("=" * 50)
    log_info("BIZmate Edge-AI Daemon Starting")
    log_info("=" * 50)

    daemon = EdgeAIDaemon()

    # Setup all components
    if not daemon.setup():
        log_error("[EdgeAIDaemon] Setup failed - exiting")
        sys.exit(1)

    # Run the daemon (blocking)
    try:
        daemon.run()
    except Exception as e:
        log_error(f"[EdgeAIDaemon] Fatal error: {e}")
        sys.exit(1)

    log_info("[EdgeAIDaemon] Exited cleanly")
    sys.exit(0)


if __name__ == "__main__":
    main()
