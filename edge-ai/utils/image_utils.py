"""
Image Processing Utilities for Edge-AI Module
Frame resizing, color conversion, bounding box drawing, image encoding
"""

import cv2
import numpy as np
from typing import Tuple, List, Optional
import base64
import io
from PIL import Image as PILImage

from .logger import log_debug, log_warning, log_error


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FRAME RESIZING & NORMALIZATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def resize_frame(frame: np.ndarray, target_width: int, target_height: int,
                 maintain_aspect: bool = True) -> np.ndarray:
    """
    Resize frame to target dimensions
    
    Args:
        frame: Input frame (BGR image from OpenCV)
        target_width: Target width in pixels
        target_height: Target height in pixels
        maintain_aspect: If True, maintain aspect ratio (pad with black borders)
    
    Returns:
        np.ndarray: Resized frame
    """
    if frame is None or frame.size == 0:
        log_warning("Cannot resize None or empty frame")
        return frame
    
    try:
        original_height, original_width = frame.shape[:2]
        
        if not maintain_aspect:
            # Simple resize (may distort)
            return cv2.resize(frame, (target_width, target_height), 
                            interpolation=cv2.INTER_LINEAR)
        
        # Maintain aspect ratio with letterboxing
        # Calculate scale to fit within target
        scale = min(target_width / original_width, target_height / original_height)
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)
        
        # Resize
        resized = cv2.resize(frame, (new_width, new_height), 
                            interpolation=cv2.INTER_LINEAR)
        
        # Create canvas and center image
        canvas = np.zeros((target_height, target_width, 3), dtype=np.uint8)
        y_offset = (target_height - new_height) // 2
        x_offset = (target_width - new_width) // 2
        canvas[y_offset:y_offset+new_height, x_offset:x_offset+new_width] = resized
        
        return canvas
    
    except Exception as e:
        log_error(f"Error resizing frame: {e}")
        return frame


def normalize_frame(frame: np.ndarray, normalize_to_01: bool = True) -> np.ndarray:
    """
    Normalize frame pixel values
    
    Args:
        frame: Input frame
        normalize_to_01: If True, normalize to [0, 1]. If False, [-1, 1]
    
    Returns:
        np.ndarray: Normalized frame (float32)
    """
    try:
        # Convert to float
        normalized = frame.astype(np.float32)
        
        if normalize_to_01:
            # Normalize to [0, 1]
            normalized = normalized / 255.0
        else:
            # Normalize to [-1, 1]
            normalized = (normalized / 127.5) - 1.0
        
        return normalized
    except Exception as e:
        log_error(f"Error normalizing frame: {e}")
        return frame.astype(np.float32)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# COLOR SPACE CONVERSION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def bgr_to_rgb(frame: np.ndarray) -> np.ndarray:
    """
    Convert OpenCV BGR frame to RGB
    
    Args:
        frame: BGR frame from OpenCV
    
    Returns:
        np.ndarray: RGB frame
    """
    if frame is None or frame.size == 0:
        return frame
    try:
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    except Exception as e:
        log_warning(f"Error converting BGR to RGB: {e}")
        return frame


def rgb_to_bgr(frame: np.ndarray) -> np.ndarray:
    """
    Convert RGB frame to OpenCV BGR
    
    Args:
        frame: RGB frame
    
    Returns:
        np.ndarray: BGR frame
    """
    if frame is None or frame.size == 0:
        return frame
    try:
        return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    except Exception as e:
        log_warning(f"Error converting RGB to BGR: {e}")
        return frame


def bgr_to_grayscale(frame: np.ndarray) -> np.ndarray:
    """
    Convert BGR frame to grayscale
    
    Args:
        frame: BGR frame
    
    Returns:
        np.ndarray: Grayscale frame
    """
    if frame is None or frame.size == 0:
        return frame
    try:
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    except Exception as e:
        log_warning(f"Error converting to grayscale: {e}")
        return frame


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BOUNDING BOX & ANNOTATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def draw_bounding_box(frame: np.ndarray, bbox: List[int], label: str = "",
                     confidence: float = None, color: Tuple[int, int, int] = (0, 255, 0),
                     thickness: int = 2) -> np.ndarray:
    """
    Draw bounding box on frame
    
    Args:
        frame: Input frame
        bbox: [x, y, width, height]
        label: Label text
        confidence: Confidence score (optional)
        color: BGR color tuple (B, G, R)
        thickness: Line thickness
    
    Returns:
        np.ndarray: Frame with drawn box
    """
    if frame is None or len(bbox) != 4:
        return frame
    
    try:
        x, y, w, h = [int(v) for v in bbox]
        
        # Clamp to frame boundaries
        frame_h, frame_w = frame.shape[:2]
        x = max(0, min(x, frame_w))
        y = max(0, min(y, frame_h))
        x2 = max(0, min(x + w, frame_w))
        y2 = max(0, min(y + h, frame_h))
        
        # Draw rectangle
        cv2.rectangle(frame, (x, y), (x2, y2), color, thickness)
        
        # Draw label if provided
        if label or confidence is not None:
            label_text = label
            if confidence is not None:
                label_text += f" ({confidence:.2f})"
            
            # Get text size for background
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5
            text_thickness = 1
            text_size = cv2.getTextSize(label_text, font, font_scale, text_thickness)[0]
            
            # Draw background rectangle
            bg_color = (255, 255, 255)  # White
            cv2.rectangle(frame, (x, y - text_size[1] - 4),
                        (x + text_size[0] + 4, y), bg_color, -1)
            
            # Draw text
            cv2.putText(frame, label_text, (x + 2, y - 2),
                       font, font_scale, (0, 0, 0), text_thickness)
        
        return frame
    
    except Exception as e:
        log_warning(f"Error drawing bounding box: {e}")
        return frame


def draw_text(frame: np.ndarray, text: str, position: Tuple[int, int],
             color: Tuple[int, int, int] = (0, 255, 0),
             font_scale: float = 0.5, thickness: int = 1) -> np.ndarray:
    """
    Draw text on frame
    
    Args:
        frame: Input frame
        text: Text to draw
        position: (x, y) position for text
        color: BGR color tuple
        font_scale: Font size scale
        thickness: Text thickness
    
    Returns:
        np.ndarray: Frame with drawn text
    """
    if frame is None:
        return frame
    
    try:
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, text, position, font, font_scale, color, thickness)
        return frame
    except Exception as e:
        log_warning(f"Error drawing text: {e}")
        return frame


def crop_roi(frame: np.ndarray, bbox: List[int]) -> Optional[np.ndarray]:
    """
    Crop region of interest from frame
    
    Args:
        frame: Input frame
        bbox: [x, y, width, height]
    
    Returns:
        np.ndarray or None: Cropped region
    """
    if frame is None or len(bbox) != 4:
        return None
    
    try:
        x, y, w, h = [int(v) for v in bbox]
        frame_h, frame_w = frame.shape[:2]
        
        # Clamp to boundaries
        x = max(0, x)
        y = max(0, y)
        x2 = min(frame_w, x + w)
        y2 = min(frame_h, y + h)
        
        if x2 > x and y2 > y:
            return frame[y:y2, x:x2]
        return None
    
    except Exception as e:
        log_warning(f"Error cropping ROI: {e}")
        return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# IMAGE ENCODING & SERIALIZATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def frame_to_jpeg_bytes(frame: np.ndarray, quality: int = 80) -> Optional[bytes]:
    """
    Encode frame as JPEG bytes
    
    Args:
        frame: Input frame (BGR)
        quality: JPEG compression quality (0-100)
    
    Returns:
        bytes or None: JPEG encoded frame
    """
    if frame is None or frame.size == 0:
        return None
    
    try:
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        success, encoded = cv2.imencode('.jpg', frame, encode_param)
        if success:
            return encoded.tobytes()
        return None
    except Exception as e:
        log_error(f"Error encoding frame to JPEG: {e}")
        return None


def frame_to_base64(frame: np.ndarray, quality: int = 80) -> Optional[str]:
    """
    Encode frame as base64 string (for sending in JSON)
    
    Args:
        frame: Input frame (BGR)
        quality: JPEG compression quality
    
    Returns:
        str or None: Base64 encoded frame
    """
    jpeg_bytes = frame_to_jpeg_bytes(frame, quality)
    if jpeg_bytes:
        try:
            return base64.b64encode(jpeg_bytes).decode('utf-8')
        except Exception as e:
            log_error(f"Error encoding to base64: {e}")
    return None


def base64_to_frame(base64_str: str) -> Optional[np.ndarray]:
    """
    Decode base64 string to frame
    
    Args:
        base64_str: Base64 encoded frame
    
    Returns:
        np.ndarray or None: Decoded frame (BGR)
    """
    if not base64_str:
        return None
    
    try:
        jpeg_bytes = base64.b64decode(base64_str)
        nparr = np.frombuffer(jpeg_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return frame
    except Exception as e:
        log_error(f"Error decoding from base64: {e}")
        return None


def save_frame_to_file(frame: np.ndarray, filepath: str, quality: int = 95) -> bool:
    """
    Save frame to file (JPEG or PNG based on extension)
    
    Args:
        frame: Input frame
        filepath: Path to save file
        quality: JPEG quality (ignored for PNG)
    
    Returns:
        bool: True if successful
    """
    if frame is None or frame.size == 0:
        log_warning("Cannot save None or empty frame")
        return False
    
    try:
        if filepath.lower().endswith('.jpg') or filepath.lower().endswith('.jpeg'):
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
            success = cv2.imwrite(filepath, frame, encode_param)
        else:
            # PNG
            success = cv2.imwrite(filepath, frame)
        
        if success:
            log_debug(f"Frame saved: {filepath}")
            return True
        return False
    
    except Exception as e:
        log_error(f"Error saving frame: {e}")
        return False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FILTERING & ENHANCEMENT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def apply_gaussian_blur(frame: np.ndarray, kernel_size: int = 5) -> np.ndarray:
    """
    Apply Gaussian blur (noise reduction)
    
    Args:
        frame: Input frame
        kernel_size: Kernel size (must be odd, e.g., 3, 5, 7)
    
    Returns:
        np.ndarray: Blurred frame
    """
    if frame is None or frame.size == 0:
        return frame
    
    try:
        if kernel_size % 2 == 0:
            kernel_size += 1
        return cv2.GaussianBlur(frame, (kernel_size, kernel_size), 0)
    except Exception as e:
        log_warning(f"Error applying blur: {e}")
        return frame


def enhance_contrast(frame: np.ndarray, alpha: float = 1.5, beta: float = 0) -> np.ndarray:
    """
    Enhance frame contrast (brightness adjustment)
    
    Args:
        frame: Input frame
        alpha: Contrast multiplier (1.0 = unchanged)
        beta: Brightness offset
    
    Returns:
        np.ndarray: Enhanced frame
    """
    if frame is None or frame.size == 0:
        return frame
    
    try:
        enhanced = cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)
        return enhanced
    except Exception as e:
        log_warning(f"Error enhancing contrast: {e}")
        return frame


def histogram_equalization(frame: np.ndarray) -> np.ndarray:
    """
    Apply histogram equalization (improve visibility)
    
    Args:
        frame: Input frame (BGR or grayscale)
    
    Returns:
        np.ndarray: Equalized frame
    """
    if frame is None or frame.size == 0:
        return frame
    
    try:
        if len(frame.shape) == 2:
            # Grayscale
            return cv2.equalizeHist(frame)
        else:
            # Color: convert to HSV, equalize V channel, convert back
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            hsv[:, :, 2] = cv2.equalizeHist(hsv[:, :, 2])
            return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    except Exception as e:
        log_warning(f"Error in histogram equalization: {e}")
        return frame


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FRAME STATISTICS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_frame_dimensions(frame: np.ndarray) -> Tuple[int, int, int]:
    """
    Get frame height, width, channels
    
    Args:
        frame: Input frame
    
    Returns:
        tuple: (height, width, channels) or (0, 0, 0) if invalid
    """
    if frame is None or frame.size == 0:
        return (0, 0, 0)
    
    try:
        h, w = frame.shape[:2]
        c = frame.shape[2] if len(frame.shape) > 2 else 1
        return (h, w, c)
    except:
        return (0, 0, 0)


def get_frame_brightness(frame: np.ndarray) -> float:
    """
    Calculate average brightness of frame (0-255)
    
    Args:
        frame: Input frame
    
    Returns:
        float: Average brightness
    """
    if frame is None or frame.size == 0:
        return 0.0
    
    try:
        gray = bgr_to_grayscale(frame)
        return float(np.mean(gray))
    except:
        return 0.0
