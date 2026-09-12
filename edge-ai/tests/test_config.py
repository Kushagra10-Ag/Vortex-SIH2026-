"""
Configuration Tests
Test configuration validation, environment variable loading, and defaults.
"""

import os
import pytest
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import EdgeAIConfig


class TestConfigValidation:
    """Test configuration validation logic."""

    def test_valid_configuration(self):
        """Test that valid configuration passes validation."""
        is_valid, errors = EdgeAIConfig.validate()
        assert is_valid is True
        assert len(errors) == 0

    def test_missing_backend_url(self):
        """Test that missing BACKEND_API_URL is caught."""
        original_url = EdgeAIConfig.BACKEND_API_URL
        EdgeAIConfig.BACKEND_API_URL = ""
        is_valid, errors = EdgeAIConfig.validate()
        EdgeAIConfig.BACKEND_API_URL = original_url
        assert is_valid is False
        assert any("BACKEND_API_URL" in error for error in errors)

    def test_missing_device_id(self):
        """Test that missing DEVICE_ID is caught."""
        original_id = EdgeAIConfig.DEVICE_ID
        EdgeAIConfig.DEVICE_ID = ""
        is_valid, errors = EdgeAIConfig.validate()
        EdgeAIConfig.DEVICE_ID = original_id
        assert is_valid is False
        assert any("DEVICE_ID" in error for error in errors)

    def test_invalid_camera_fps(self):
        """Test that invalid CAMERA_FPS is caught."""
        original_fps = EdgeAIConfig.CAMERA_FPS
        EdgeAIConfig.CAMERA_FPS = 150  # Invalid (> 120)
        is_valid, errors = EdgeAIConfig.validate()
        EdgeAIConfig.CAMERA_FPS = original_fps
        assert is_valid is False
        assert any("CAMERA_FPS" in error for error in errors)

    def test_invalid_camera_resolution(self):
        """Test that invalid camera resolution is caught."""
        original_width = EdgeAIConfig.CAMERA_WIDTH
        EdgeAIConfig.CAMERA_WIDTH = -100  # Invalid
        is_valid, errors = EdgeAIConfig.validate()
        EdgeAIConfig.CAMERA_WIDTH = original_width
        assert is_valid is False
        assert any("resolution" in error.lower() for error in errors)

    def test_invalid_confidence_threshold(self):
        """Test that invalid confidence threshold is caught."""
        original_conf = EdgeAIConfig.MODEL_CONFIDENCE_THRESHOLD
        EdgeAIConfig.MODEL_CONFIDENCE_THRESHOLD = 1.5  # Invalid (> 1.0)
        is_valid, errors = EdgeAIConfig.validate()
        EdgeAIConfig.MODEL_CONFIDENCE_THRESHOLD = original_conf
        assert is_valid is False
        assert any("MODEL_CONFIDENCE_THRESHOLD" in error for error in errors)


class TestConfigDefaults:
    """Test that configuration defaults are sensible."""

    def test_backend_api_url_default(self):
        """Test default backend API URL."""
        assert EdgeAIConfig.BACKEND_API_URL == "http://127.0.0.1:5000"

    def test_device_id_default(self):
        """Test default device ID."""
        assert EdgeAIConfig.DEVICE_ID == "edge-ai-device-001"

    def test_camera_source_default(self):
        """Test default camera source."""
        assert EdgeAIConfig.CAMERA_SOURCE == "0"

    def test_queue_threshold_default(self):
        """Test default queue length threshold is 3 as specified."""
        assert EdgeAIConfig.QUEUE_LENGTH_THRESHOLD == 3

    def test_use_mock_sensors_default(self):
        """Test default is to use mock sensors."""
        assert EdgeAIConfig.USE_MOCK_SENSORS is True

    def test_heartbeat_interval_default(self):
        """Test default heartbeat interval."""
        assert EdgeAIConfig.HEARTBEAT_INTERVAL_SECONDS == 60


class TestConfigToDict:
    """Test configuration export to dictionary."""

    def test_to_dict_structure(self):
        """Test that to_dict returns expected structure."""
        config_dict = EdgeAIConfig.to_dict()
        assert isinstance(config_dict, dict)
        assert "backend_api_url" in config_dict
        assert "device_id" in config_dict
        assert "camera_source" in config_dict
        assert "yolo_model" in config_dict
        assert "sensors" in config_dict

    def test_to_dict_sensors_section(self):
        """Test that sensors section has expected keys."""
        config_dict = EdgeAIConfig.to_dict()
        sensors = config_dict["sensors"]
        assert "use_mock" in sensors
        assert "dht22" in sensors
        assert "hx711" in sensors
        assert "pir" in sensors
        assert "ultrasonic" in sensors


class TestEnvironmentLoading:
    """Test environment variable loading."""

    def test_env_file_loading(self):
        """Test that .env file is loaded if present."""
        # This test assumes .env might exist in development
        # In CI/testing, we might not have .env, so we just check no crash
        try:
            from config import EdgeAIConfig
            config = EdgeAIConfig()
            assert config is not None
        except Exception as e:
            pytest.fail(f"Config loading failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
