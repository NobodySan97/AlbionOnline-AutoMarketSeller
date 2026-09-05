"""
OCR number parser, binary detection, and image preprocessing using OpenCV and Tesseract.
"""

import os
import re
import shutil
from collections import Counter
import cv2
import numpy as np
from PIL import Image, ImageGrab
import pytesseract


def parse_albion_number(text: str) -> int | None:
    """Parses raw OCR number string with robust European/American format handling."""
    if not text:
        return None

    text = text.strip()
    text = re.sub(r"[^\w.,]", "", text)

    text = text.replace("O", "0").replace("o", "0")
    text = text.replace("l", "1").replace("I", "1")
    text = text.replace("S", "5").replace("s", "5")
    text = text.replace("B", "8")

    match = re.search(r"([\d.,]+)\s*([KkMmtT])?", text)
    if not match:
        return None

    num_part, suffix = match.groups()
    suffix = suffix.upper() if suffix else None

    num_part = num_part.strip(".,")
    if not num_part:
        return None

    dot_count = num_part.count(".")
    comma_count = num_part.count(",")

    if dot_count > 0 and comma_count > 0:
        last_dot = num_part.rfind(".")
        last_comma = num_part.rfind(",")
        if last_dot > last_comma:
            clean_str = num_part.replace(",", "")
            val = float(clean_str)
        else:
            clean_str = num_part.replace(".", "").replace(",", ".")
            val = float(clean_str)
    elif dot_count > 1:
        clean_str = num_part.replace(".", "")
        val = float(clean_str)
    elif comma_count > 1:
        clean_str = num_part.replace(",", "")
        val = float(clean_str)
    elif dot_count == 1:
        parts = num_part.split(".")
        if suffix:
            val = float(num_part)
        elif len(parts[1]) == 3:
            val = float(parts[0] + parts[1])
        else:
            val = float(num_part)
    elif comma_count == 1:
        parts = num_part.split(",")
        if suffix:
            val = float(parts[0] + "." + parts[1])
        elif len(parts[1]) == 3:
            val = float(parts[0] + parts[1])
        else:
            val = float(parts[0] + "." + parts[1])
    else:
        try:
            val = float(num_part)
        except ValueError:
            return None

    if suffix == "K":
        val *= 1_000
    elif suffix == "M":
        val *= 1_000_000
    elif suffix == "T":
        val *= 1_000

    return int(round(val))


def detect_tesseract_binary(custom_path: str = "") -> str:
    """Locates Tesseract OCR executable across common Windows installation paths."""
    candidate_paths = [
        custom_path,
        shutil.which("tesseract"),
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tesseract", "tesseract.exe"),
    ]
    for p in candidate_paths:
        if p and os.path.isfile(p):
            return os.path.abspath(p)
    return ""


class OcrReader:
    """Preprocesses cropped regions and executes Tesseract OCR for numerical price detection."""

    @staticmethod
    def preprocess_image(pil_image: Image.Image) -> list[Image.Image]:
        img_np = np.array(pil_image)
        if len(img_np.shape) == 3:
            gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_np

        scale = 3.0
        width = int(gray.shape[1] * scale)
        height = int(gray.shape[0] * scale)
        resized = cv2.resize(gray, (width, height), interpolation=cv2.INTER_CUBIC)

        variants = []
        block_size = max(15, (resized.shape[0] // 4) * 2 + 1)
        blurred = cv2.GaussianBlur(resized, (3, 3), 0)
        thresh_adapt = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, 3
        )
        variants.append(Image.fromarray(thresh_adapt))
        variants.append(Image.fromarray(cv2.bitwise_not(thresh_adapt)))

        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        contrast = clahe.apply(resized)
        _, thresh_otsu = cv2.threshold(contrast, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        variants.append(Image.fromarray(thresh_otsu))
        variants.append(Image.fromarray(cv2.bitwise_not(thresh_otsu)))

        return variants

    @classmethod
    def read_number_from_bbox(
        cls, bbox: tuple[int, int, int, int], whitelist: str = "0123456789.,kKmMtT"
    ) -> int | None:
        x1, y1, x2, y2 = bbox
        if x2 <= x1 or y2 <= y1:
            return None

        grab = None
        variants = []
        try:
            grab = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            variants = cls.preprocess_image(grab)

            psm_configs = ["--psm 7", "--psm 8", "--psm 6"]
            results = []
            for i, img in enumerate(variants):
                psm = psm_configs[i % len(psm_configs)]
                tess_config = f"{psm} -c tessedit_char_whitelist={whitelist}"
                try:
                    raw_text = pytesseract.image_to_string(img, config=tess_config).strip()
                    parsed = parse_albion_number(raw_text)
                    if parsed is not None and parsed > 0:
                        results.append(parsed)
                        # Fast-path short-circuit: if first adaptive variant gives high-confidence number, return immediately
                        if i == 0 and parsed >= 10:
                            return parsed
                        if len(results) >= 2 and results[-1] == results[-2]:
                            return results[-1]
                except Exception:
                    pass

            if not results:
                return None

            return Counter(results).most_common(1)[0][0]
        except Exception:
            return None
        finally:
            if grab is not None:
                try:
                    grab.close()
                except Exception:
                    pass
            for v in variants:
                try:
                    if hasattr(v, "close"):
                        v.close()
                except Exception:
                    pass
            del variants


class TemplateMatcher:
    """Template matching using OpenCV for visual UI anchors (backward-compatible)."""

    @staticmethod
    def find_template_in_image(
        image: np.ndarray,
        template_path: str,
        threshold: float = 0.8,
        scales: list[float] | None = None,
    ) -> tuple[tuple[int, int] | None, float]:
        if not os.path.isfile(template_path):
            return None, 0.0

        template = cv2.imread(template_path, cv2.IMREAD_COLOR)
        if template is None:
            return None, 0.0

        if scales is None:
            scales = [1.0]

        best_max_val = -1.0
        best_center = None

        img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image

        for scale in scales:
            if scale == 1.0:
                t_scaled = template
            else:
                w = int(template.shape[1] * scale)
                h = int(template.shape[0] * scale)
                if w <= 0 or h <= 0 or w > image.shape[1] or h > image.shape[0]:
                    continue
                t_scaled = cv2.resize(template, (w, h), interpolation=cv2.INTER_AREA)

            t_gray = cv2.cvtColor(t_scaled, cv2.COLOR_BGR2GRAY) if len(t_scaled.shape) == 3 else t_scaled

            if t_gray.shape[0] > img_gray.shape[0] or t_gray.shape[1] > img_gray.shape[1]:
                continue

            res = cv2.matchTemplate(img_gray, t_gray, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)

            if max_val > best_max_val:
                best_max_val = max_val
                cx = max_loc[0] + t_scaled.shape[1] // 2
                cy = max_loc[1] + t_scaled.shape[0] // 2
                best_center = (cx, cy)

        if best_max_val >= threshold:
            return best_center, float(best_max_val)
        return None, 0.0
