import os
import sys
import numpy as np
import cv2

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from AutoSeller import TemplateMatcher


def test_template_matcher_synthetic(tmp_path):
    # Create a synthetic canvas
    canvas = np.zeros((400, 600, 3), dtype=np.uint8)
    canvas[:] = (30, 30, 30)  # dark gray background

    # Draw a unique button pattern at (200, 150)
    btn_color = (0, 180, 255)  # orange/gold
    cv2.rectangle(canvas, (200, 150), (280, 190), btn_color, -1)
    cv2.putText(canvas, "SELL", (210, 178), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    # Save template crop (80x40)
    template_crop = canvas[150:190, 200:280]
    template_path = str(tmp_path / "sell_button.png")
    cv2.imwrite(template_path, template_crop)

    # Test matching on the canvas
    center, conf = TemplateMatcher.find_template_in_image(canvas, template_path, threshold=0.8)

    assert center is not None
    assert conf >= 0.95
    # Center should be at 200 + 40 = 240, 150 + 20 = 170
    assert abs(center[0] - 240) <= 2
    assert abs(center[1] - 170) <= 2


def test_template_matcher_missing_file():
    center, conf = TemplateMatcher.find_template_in_image(
        np.zeros((100, 100, 3), dtype=np.uint8), "non_existent_file.png"
    )
    assert center is None
    assert conf == 0.0
