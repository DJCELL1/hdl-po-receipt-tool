"""
Image preprocessing for OCR optimization
Handles deskewing, thresholding, denoising
"""

import cv2
import numpy as np
from PIL import Image
import logging

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Preprocesses images for optimal OCR results"""

    @staticmethod
    def load_image(image_path: str) -> np.ndarray:
        """Load image from file path"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Could not load image: {image_path}")
            return img
        except Exception as e:
            logger.error(f"Error loading image: {e}")
            raise

    @staticmethod
    def convert_to_grayscale(img: np.ndarray) -> np.ndarray:
        """Convert image to grayscale"""
        if len(img.shape) == 3:
            return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return img

    @staticmethod
    def deskew(img: np.ndarray) -> np.ndarray:
        """
        Automatically deskew image using Hough line transform
        Corrects for rotated/tilted documents
        """
        gray = ImageProcessor.convert_to_grayscale(img)

        # Detect edges
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)

        # Detect lines using Hough transform
        lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)

        if lines is None:
            logger.info("No lines detected for deskewing")
            return img

        # Calculate dominant angle
        angles = []
        for rho, theta in lines[:, 0]:
            angle = np.degrees(theta) - 90
            if -45 < angle < 45:
                angles.append(angle)

        if not angles:
            return img

        median_angle = np.median(angles)
        logger.info(f"Deskewing by {median_angle:.2f} degrees")

        # Rotate image
        (h, w) = img.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
        rotated = cv2.warpAffine(
            img, M, (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE
        )

        return rotated

    @staticmethod
    def denoise(img: np.ndarray) -> np.ndarray:
        """Apply denoising filter"""
        gray = ImageProcessor.convert_to_grayscale(img)
        return cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)

    @staticmethod
    def apply_threshold(img: np.ndarray, method: str = "adaptive") -> np.ndarray:
        """
        Apply thresholding to create binary image
        Methods: 'adaptive', 'otsu', 'binary'
        """
        gray = ImageProcessor.convert_to_grayscale(img)

        if method == "adaptive":
            # Adaptive threshold - works well for varying lighting
            return cv2.adaptiveThreshold(
                gray, 255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11, 2
            )
        elif method == "otsu":
            # Otsu's method - automatic threshold
            _, binary = cv2.threshold(
                gray, 0, 255,
                cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )
            return binary
        else:
            # Simple binary threshold
            _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            return binary

    @staticmethod
    def enhance_contrast(img: np.ndarray) -> np.ndarray:
        """Enhance contrast using CLAHE"""
        gray = ImageProcessor.convert_to_grayscale(img)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(gray)

    @staticmethod
    def remove_borders(img: np.ndarray, border_percent: float = 0.02) -> np.ndarray:
        """Remove borders from image (can contain noise)"""
        h, w = img.shape[:2]
        border_h = int(h * border_percent)
        border_w = int(w * border_percent)

        return img[border_h:h - border_h, border_w:w - border_w]

    @staticmethod
    def preprocess_for_ocr(image_path: str, aggressive: bool = False) -> np.ndarray:
        """
        Complete preprocessing pipeline for OCR
        Args:
            image_path: Path to input image
            aggressive: Use more aggressive preprocessing (for poor quality images)
        Returns:
            Preprocessed image ready for OCR
        """
        logger.info(f"Preprocessing image: {image_path}")

        # Load image
        img = ImageProcessor.load_image(image_path)

        # Remove borders
        img = ImageProcessor.remove_borders(img)

        # Deskew
        img = ImageProcessor.deskew(img)

        if aggressive:
            # Aggressive mode for poor quality images
            img = ImageProcessor.denoise(img)
            img = ImageProcessor.enhance_contrast(img)
            img = ImageProcessor.apply_threshold(img, method="adaptive")
        else:
            # Standard mode
            img = ImageProcessor.enhance_contrast(img)
            img = ImageProcessor.apply_threshold(img, method="otsu")

        logger.info("Preprocessing complete")
        return img

    @staticmethod
    def save_image(img: np.ndarray, output_path: str):
        """Save processed image"""
        cv2.imwrite(output_path, img)
        logger.info(f"Saved processed image to: {output_path}")
