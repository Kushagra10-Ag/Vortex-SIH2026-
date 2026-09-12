# Backend and Edge-AI Todo List

This list is based on the current repository inspection and the camera connectivity checks performed on 2026-09-12. Items marked `Needs verification` are not treated as confirmed defects until the relevant runtime or hardware condition is available.

## Confirmed blockers

- [x] Fix backend model loading in `backend/app/services/ai_service.py`: remove the machine-specific absolute path and resolve `sales_model.pkl` relative to the repository or an environment variable.
- [x] Decide whether the sales model is optional. Backend app creation currently fails if the model file is absent, even for routes that do not use forecasting.
- [x] Normalize edge-ai package imports. The daemon imports `ai`, `camera`, `events`, and similar modules as top-level packages, while their files use parent-relative imports such as `..utils`. Choose one package execution model and apply it consistently.
- [x] Make the documented `edge-ai/python app.py` launch path work, or update the documentation to the supported module invocation.
- [x] Repair backend controller/service API mismatches for monitoring, sensors, devices, and alerts.
- [x] Add one consistent serialization mechanism for backend models. Current services call `.to_dict()` on models that do not define it.
- [x] Align camera event payload names between edge-ai and backend. The edge sends fields such as `camera_id` and `bbox_coordinates`, while backend persistence uses `device_id` and `details`.
- [x] Align event type names used by edge-ai and backend dashboard helpers, especially queue events.
- [x] Add authentication or a dedicated device credential check to telemetry ingestion and device-management routes.
- [x] Restrict CORS to configured frontend origins instead of enabling unrestricted CORS.
- [x] Move database credentials and JWT/secret defaults out of source-controlled configuration. Require environment configuration outside local development.
- [x] Fix the edge-ai test import setup and make the test suite collect successfully.

## Camera integration

- [x] Start the IP Webcam server on the phone and confirm it is listening on the displayed address.
- [x] Confirm the phone and edge host are on the same reachable network and that the phone firewall/security settings allow inbound TCP `8080`.
- [x] Re-test `http://10.12.43.218:8080` after the server is started.
- [x] Verify the actual stream endpoint before configuring the daemon. The verified stream is `/videofeed`; `/shot.jpg` also returns a JPEG snapshot.
- [x] Test the confirmed stream with OpenCV through `edge-ai/camera/mobile_camera.py` and `edge-ai/camera/stream_handler.py`.
- [x] Set `CAMERA_SOURCE` in an untracked `edge-ai/.env` only after the endpoint is verified. Configured value: `http://10.12.43.218:8080/videofeed`.
- [x] Capture one frame and verify dimensions, color format, and frame freshness before enabling inference.
- [x] Tune `CAMERA_WIDTH`, `CAMERA_HEIGHT`, `CAMERA_FPS`, and warmup settings against the phone stream.
- [x] Confirm reconnect behavior by stopping and restarting the phone stream.

## Edge-AI runtime correctness

- [x] Run inference once per frame and share the detections with people, queue, and shelf detectors, instead of invoking the shared inference engine independently for each detector.
- [x] Use independent tracker state for people occupancy and queue tracking, or explicitly prove that shared tracking is safe.
- [x] Replace hard-coded queue and shelf ROIs with configuration validated against the actual camera resolution and view.
- [ ] Verify shelf class IDs and default ROIs against the real store layout; current defaults are assumptions.
- [x] Verify that sensor readings and footfall events match the backend schema, including timestamps, sensor IDs, occupancy, and anomaly fields.
- [x] Verify offline buffering, retry limits, duplicate handling, and ordering after backend recovery.
- [x] Ensure graceful shutdown stops the heartbeat thread and joins all worker threads cleanly.

## Backend behavior and contracts

- [x] Add request validation for device registration, camera events, sensor readings, footfall, alerts, and shelf updates.
- [x] Add integration tests that exercise every edge-ingestion route with representative edge payloads.
- [x] Add dashboard contract tests for the response shapes documented in `design.md` and consumed by `frontend/services/api.ts`.
- [x] Resolve the dashboard response-shape discrepancy (`data` versus the documented `dashboard` field).
- [x] Define and enforce one vocabulary for shelf states (`low` versus `low_stock`) and queue event names.
- [x] Add stale-device processing or a scheduled mechanism for marking devices offline after missed heartbeats.
- [x] Add database migration verification for all telemetry tables and relationships.
- [x] Add rate limits and payload-size limits for public or device-facing ingestion endpoints, especially snapshot-bearing camera events.

## Validation checklist

- [x] `python -c "from app import create_app; create_app()"` succeeds from `backend/`.
- [x] `python -m pytest -q` succeeds from `edge-ai/`.
- [ ] `python app.py` reaches daemon setup from `edge-ai/` with a reachable backend and verified camera stream.
- [ ] A real camera frame reaches the edge pipeline.
- [ ] A camera event, sensor reading, footfall record, heartbeat, and alert can each be persisted and read back through the backend API.
- [ ] Frontend dashboard data renders from the actual backend response without adapter-specific assumptions.

## Camera check result

- Image-observed base URLs: `http://10.12.43.218:8080` and `https://10.12.43.218:8080`.
- Host ping: succeeded.
- TCP `10.12.43.218:8080`: failed.
- HTTP probes attempted: `/`, `/video`, `/shot.jpg`, `/video.mjpg`, `/videofeed`; all were unreachable.
- Conclusion: the camera was not connected at the application level during this check. No stream URL was configured and no claim of successful video access is made.
- Recheck: local host `10.12.44.36/16` and camera host `10.12.43.218` are on the same apparent network and the host responds to ping, but TCP `8080` remains closed.
- Latest camera recheck: ping still succeeds, TCP `8080` still fails, and `/`, `/video`, `/shot.jpg`, `/video.mjpg`, and `/videofeed` remain unavailable. IP Webcam must be started on the phone before these items can be completed.
- Current camera check: TCP `8080` is open, `/` returns 200, `/shot.jpg` returns `image/jpeg`, `/videofeed` returns `multipart/x-mixed-replace`, and `/video.mjpg` returns 404. The verified stream endpoint is `http://10.12.43.218:8080/videofeed`.
- Live OpenCV check: `VideoCapture` opened `/videofeed` and captured a `1920x1080`, 3-channel, `uint8` BGR frame. The configured processing output is `1280x720`; the wrapper opened successfully on two stop/start cycles, although the zero-wait threaded probe did not observe a buffered frame.
- OpenCV probe: unavailable because `cv2` is not installed in the active interpreter; no frame was captured.
- Shelf configuration check: COCO IDs `[39, 41]`, `[46, 47]`, and `[67, 72]` map to bottle/cup, banana/apple, and cell phone/toothbrush; all default ROIs fit within `1280x720`. Real-store layout suitability remains unverified.