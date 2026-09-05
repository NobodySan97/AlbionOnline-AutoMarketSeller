"""
Human-like mouse movement and typing simulation.
"""

import math
import random
import time
import pyautogui

# Disable PyAutoGUI artificial pause to allow smooth, high-fps mouse trajectories
pyautogui.PAUSE = 0.0
pyautogui.FAILSAFE = False


def generate_bezier_curve(
    start: tuple[int, int], end: tuple[int, int], num_points: int = 25, deviation: int = 30
) -> list[tuple[int, int]]:
    """Generates smooth human-like cubic Bézier curve trajectory."""
    x0, y0 = start
    x3, y3 = end

    dx = x3 - x0
    dy = y3 - y0
    dist = math.hypot(dx, dy)

    if dist < 5:
        return [(int(x3), int(y3))]

    nx = -dy / dist
    ny = dx / dist

    offset1 = random.uniform(-deviation, deviation)
    offset2 = random.uniform(-deviation, deviation)

    x1 = int(x0 + dx * 0.33 + nx * offset1)
    y1 = int(y0 + dy * 0.33 + ny * offset1)
    x2 = int(x0 + dx * 0.66 + nx * offset2)
    y2 = int(y0 + dy * 0.66 + ny * offset2)

    points = []
    for i in range(num_points):
        t_raw = i / max(1, num_points - 1)
        t = 0.5 * (1 - math.cos(math.pi * t_raw))

        bx = (1 - t) ** 3 * x0 + 3 * (1 - t) ** 2 * t * x1 + 3 * (1 - t) * t**2 * x2 + t**3 * x3
        by = (1 - t) ** 3 * y0 + 3 * (1 - t) ** 2 * t * y1 + 3 * (1 - t) * t**2 * x2 + t**3 * y3
        points.append((int(round(bx)), int(round(by))))
    return points


def get_gaussian_delay(min_val: float, max_val: float) -> float:
    """Returns random delay sampled from bounded Gaussian distribution."""
    mu = (min_val + max_val) / 2.0
    sigma = (max_val - min_val) / 6.0
    val = random.gauss(mu, sigma)
    return max(min_val, min(max_val, val))


def human_move_to(target_x: int, target_y: int, enabled: bool = True):
    """Moves mouse naturally using Bézier curves with 1ms Windows timer precision."""
    if not enabled:
        pyautogui.moveTo(target_x, target_y)
        return

    current_pos = pyautogui.position()
    dist = math.hypot(target_x - current_pos[0], target_y - current_pos[1])
    if dist < 4:
        pyautogui.moveTo(target_x, target_y)
        return

    num_pts = max(8, min(28, int(dist / 25)))
    curve = generate_bezier_curve(current_pos, (target_x, target_y), num_points=num_pts)

    for pt in curve:
        pyautogui.moveTo(pt[0], pt[1])
        time.sleep(random.uniform(0.002, 0.005))
    pyautogui.moveTo(target_x, target_y)


def human_type(text: str, enabled: bool = True):
    """Types characters with natural randomized keystroke intervals."""
    if not enabled:
        pyautogui.write(text, interval=0.0)
        return
    for ch in text:
        pyautogui.write(ch)
        time.sleep(random.uniform(0.015, 0.040))
