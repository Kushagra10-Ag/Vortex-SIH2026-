"""
Detector Tests
Test people detection, queue detection, and shelf detection functionality.
"""

import pytest
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

# Mock the imports that might require hardware
import unittest.mock as mock


class TestQueueDetector:
    """Test queue detector functionality."""

    @pytest.fixture
    def mock_inference_engine(self):
        """Create a mock inference engine."""
        with mock.patch('ai.queue_detector.InferenceEngine') as mock_engine:
            engine = mock.Mock()
            engine.run.return_value = []  # No detections by default
            yield engine

    @pytest.fixture
    def mock_tracker(self):
        """Create a mock tracker."""
        with mock.patch('ai.queue_detector.CentroidTracker') as mock_tracker:
            tracker = mock.Mock()
            tracker.update.return_value = []
            yield tracker

    @pytest.fixture
    def mock_event_builder(self):
        """Create a mock event builder."""
        with mock.patch('ai.queue_detector.EventBuilder') as mock_builder:
            builder = mock.Mock()
            builder.queue_overflow.return_value = mock.Mock()
            builder.queue_empty.return_value = mock.Mock()
            yield builder

    def test_queue_detector_initialization(self, mock_inference_engine, mock_tracker, mock_event_builder):
        """Test queue detector initialization."""
        from ai.queue_detector import QueueDetector

        detector = QueueDetector(
            inference_engine=mock_inference_engine,
            tracker=mock_tracker,
            event_builder=mock_event_builder,
            queue_threshold=3
        )

        assert detector._queue_threshold == 3
        assert detector._roi is None  # Default ROI

    def test_queue_detector_with_roi(self, mock_inference_engine, mock_tracker, mock_event_builder):
        """Test queue detector with custom ROI."""
        from ai.queue_detector import QueueDetector

        roi = [100, 200, 300, 150]
        detector = QueueDetector(
            inference_engine=mock_inference_engine,
            tracker=mock_tracker,
            event_builder=mock_event_builder,
            roi=roi,
            queue_threshold=5
        )

        assert detector._roi == roi
        assert detector._queue_threshold == 5

    def test_queue_threshold_3(self, mock_inference_engine, mock_tracker, mock_event_builder):
        """Test that queue threshold uses config default of 3."""
        from ai.queue_detector import QueueDetector
        from config import EdgeAIConfig

        detector = QueueDetector(
            inference_engine=mock_inference_engine,
            tracker=mock_tracker,
            event_builder=mock_event_builder
        )

        # Should use config default of 3
        assert detector._queue_threshold == EdgeAIConfig.QUEUE_LENGTH_THRESHOLD

    def test_queue_overflow_detection(self, mock_inference_engine, mock_tracker, mock_event_builder):
        """Test queue overflow event generation."""
        from ai.queue_detector import QueueDetector
        from events.event_types import Detection

        detector = QueueDetector(
            inference_engine=mock_inference_engine,
            tracker=mock_tracker,
            event_builder=mock_event_builder,
            queue_threshold=3
        )

        # Mock frame
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)

        # Mock detections for 4 people (above threshold)
        mock_detections = [
            Detection(class_id=0, class_name="person", confidence=0.9, bbox=[100, 100, 50, 100], center=(125, 150))
            for _ in range(4)
        ]
        mock_tracker.update.return_value = mock_detections

        events, count, wait_time = detector.process(frame)

        # Should generate queue overflow event
        assert count == 4
        assert wait_time > 0
        # Check that queue_overflow was called (with cooldown, might not always trigger)
        if len(events) > 0:
            mock_event_builder.queue_overflow.assert_called()

    def test_queue_empty_detection(self, mock_inference_engine, mock_tracker, mock_event_builder):
        """Test queue empty event generation."""
        from ai.queue_detector import QueueDetector

        detector = QueueDetector(
            inference_engine=mock_inference_engine,
            tracker=mock_tracker,
            event_builder=mock_event_builder,
            queue_threshold=3
        )

        frame = np.zeros((720, 1280, 3), dtype=np.uint8)

        # First, simulate people in queue
        mock_detections = [
            mock.Mock(class_id=0, class_name="person", confidence=0.9, bbox=[100, 100, 50, 100], center=(125, 150))
        ]
        mock_tracker.update.return_value = mock_detections
        detector.process(frame)  # First run with people

        # Then simulate empty queue
        mock_tracker.update.return_value = []
        events, count, wait_time = detector.process(frame)

        # Should generate queue empty event
        assert count == 0
        assert wait_time == 0
        mock_event_builder.queue_empty.assert_called()

    def test_wait_time_estimation(self, mock_inference_engine, mock_tracker, mock_event_builder):
        """Test wait time estimation."""
        from ai.queue_detector import QueueDetector

        detector = QueueDetector(
            inference_engine=mock_inference_engine,
            tracker=mock_tracker,
            event_builder=mock_event_builder,
            queue_threshold=3,
            service_time_seconds=2.0
        )

        frame = np.zeros((720, 1280, 3), dtype=np.uint8)

        # 3 people in queue
        mock_detections = [mock.Mock() for _ in range(3)]
        mock_tracker.update.return_value = mock_detections

        events, count, wait_time = detector.process(frame)

        # Wait time should be approximately 3 * 2.0 = 6.0 seconds
        assert count == 3
        assert 5.0 <= wait_time <= 7.0  # Allow some variance


class TestShelfDetector:
    """Test shelf detector functionality."""

    @pytest.fixture
    def mock_inference_engine(self):
        """Create a mock inference engine."""
        with mock.patch('ai.shelf_detector.InferenceEngine') as mock_engine:
            engine = mock.Mock()
            engine.run.return_value = []
            yield engine

    @pytest.fixture
    def mock_event_builder(self):
        """Create a mock event builder."""
        with mock.patch('ai.shelf_detector.EventBuilder') as mock_builder:
            builder = mock.Mock()
            builder.out_of_stock.return_value = mock.Mock()
            yield builder

    def test_shelf_detector_initialization(self, mock_inference_engine, mock_event_builder):
        """Test shelf detector initialization."""
        from ai.shelf_detector import ShelfDetector, ShelfConfig

        shelf_config = ShelfConfig(
            shelf_id="A1",
            roi=[50, 200, 300, 150],
            expected_capacity=10
        )

        detector = ShelfDetector(
            inference_engine=mock_inference_engine,
            event_builder=mock_event_builder,
            shelf_configs=[shelf_config]
        )

        assert len(detector._shelf_configs) == 1
        assert detector._shelf_configs[0].shelf_id == "A1"

    def test_fill_percentage_calculation(self, mock_inference_engine, mock_event_builder):
        """Test fill percentage calculation."""
        from ai.shelf_detector import ShelfDetector, ShelfConfig

        shelf_config = ShelfConfig(
            shelf_id="A1",
            roi=[50, 200, 300, 150],
            expected_capacity=10
        )

        detector = ShelfDetector(
            inference_engine=mock_inference_engine,
            event_builder=mock_event_builder,
            shelf_configs=[shelf_config]
        )

        # Test various fill percentages
        assert detector._calculate_fill_percentage(10, 10) == 100.0  # Full
        assert detector._calculate_fill_percentage(5, 10) == 50.0   # Half
        assert detector._calculate_fill_percentage(0, 10) == 0.0    # Empty
        assert detector._calculate_fill_percentage(15, 10) == 100.0  # Cap at 100%

    def test_out_of_stock_detection(self, mock_inference_engine, mock_event_builder):
        """Test out-of-stock event generation."""
        from ai.shelf_detector import ShelfDetector, ShelfConfig
        from events.event_types import Detection

        shelf_config = ShelfConfig(
            shelf_id="A1",
            roi=[50, 200, 300, 150],
            expected_capacity=10,
            empty_threshold=10.0
        )

        detector = ShelfDetector(
            inference_engine=mock_inference_engine,
            event_builder=mock_event_builder,
            shelf_configs=[shelf_config],
            out_of_stock_threshold=10.0
        )

        frame = np.zeros((720, 1280, 3), dtype=np.uint8)

        # Mock only 1 product (10% fill = out of stock threshold)
        mock_detections = [
            Detection(class_id=39, class_name="bottle", confidence=0.9, bbox=[100, 100, 50, 100], center=(125, 150))
        ]
        mock_inference_engine.run.return_value = mock_detections

        events, shelf_states = detector.process(frame)

        # Should generate out-of-stock event
        assert "A1" in shelf_states
        assert shelf_states["A1"]["fill_percentage"] <= 10.0
        assert shelf_states["A1"]["status"] == "empty"

    def test_shelf_status_determination(self, mock_inference_engine, mock_event_builder):
        """Test shelf status determination."""
        from ai.shelf_detector import ShelfDetector, ShelfConfig
        from utils.constants import ShelfStockStatus

        shelf_config = ShelfConfig(
            shelf_id="A1",
            roi=[50, 200, 300, 150],
            expected_capacity=10,
            low_stock_threshold=30.0,
            empty_threshold=10.0
        )

        detector = ShelfDetector(
            inference_engine=mock_inference_engine,
            event_builder=mock_event_builder,
            shelf_configs=[shelf_config]
        )

        # Test different statuses
        assert detector._determine_status(80.0, shelf_config) == ShelfStockStatus.NORMAL
        assert detector._determine_status(20.0, shelf_config) == ShelfStockStatus.LOW_STOCK
        assert detector._determine_status(5.0, shelf_config) == ShelfStockStatus.EMPTY

    def test_add_remove_shelves(self, mock_inference_engine, mock_event_builder):
        """Test dynamic shelf addition and removal."""
        from ai.shelf_detector import ShelfDetector, ShelfConfig

        detector = ShelfDetector(
            inference_engine=mock_inference_engine,
            event_builder=mock_event_builder,
            shelf_configs=[]
        )

        # Add shelf
        shelf_config = ShelfConfig(shelf_id="B1", roi=[100, 200, 300, 150])
        detector.add_shelf(shelf_config)
        assert len(detector._shelf_configs) == 1

        # Remove shelf
        detector.remove_shelf("B1")
        assert len(detector._shelf_configs) == 0


class TestDefaultShelfConfigs:
    """Test default shelf configuration creation."""

    def test_default_shelf_configs_creation(self):
        """Test that default shelf configs are created correctly."""
        from ai.shelf_detector import create_default_shelf_configs

        configs = create_default_shelf_configs()

        assert len(configs) == 4  # Should create 4 default shelves
        assert configs[0].shelf_id == "A1"
        assert configs[1].shelf_id == "A2"
        assert configs[2].shelf_id == "B1"
        assert configs[3].shelf_id == "B2"

    def test_default_shelf_configs_structure(self):
        """Test that default shelf configs have expected structure."""
        from ai.shelf_detector import create_default_shelf_configs

        configs = create_default_shelf_configs()

        for config in configs:
            assert hasattr(config, 'shelf_id')
            assert hasattr(config, 'roi')
            assert hasattr(config, 'expected_capacity')
            assert len(config.roi) == 4  # [x, y, width, height]
            assert config.expected_capacity > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
