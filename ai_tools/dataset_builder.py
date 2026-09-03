"""
Albion Online AI Synthetic Dataset Builder
Downloads item data from ao-bin-dumps, fetches official renders from render.albiononline.com,
and generates synthetic annotated inventory datasets for YOLOv8/v11 training.
"""

import json
import os
import random
import sys
import urllib.request
from typing import Dict, List, Optional, Tuple
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

DUMPS_ITEMS_URL = "https://raw.githubusercontent.com/ao-data/ao-bin-dumps/master/formatted/items.json"
RENDER_BASE_URL = "https://render.albiononline.com/v1/item"


class AlbionDatasetBuilder:
    """Manages downloading Albion metadata and synthesizing training images."""

    def __init__(self, data_dir: str = "ai_data"):
        self.data_dir = data_dir
        self.renders_dir = os.path.join(data_dir, "renders")
        self.dataset_dir = os.path.join(data_dir, "dataset")
        self.items_file = os.path.join(data_dir, "items.json")

        os.makedirs(self.renders_dir, exist_ok=True)
        os.makedirs(self.dataset_dir, exist_ok=True)
        self.items: List[Dict] = []

    def download_items_database(self, force: bool = False) -> List[Dict]:
        """Downloads items.json from ao-bin-dumps if not cached."""
        if not force and os.path.isfile(self.items_file):
            try:
                with open(self.items_file, "r", encoding="utf-8") as f:
                    self.items = json.load(f)
                return self.items
            except Exception:
                pass

        req = urllib.request.Request(DUMPS_ITEMS_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read().decode("utf-8")
            self.items = json.loads(content)

        with open(self.items_file, "w", encoding="utf-8") as f:
            f.write(content)
        return self.items

    def filter_tradeable_items(
        self,
        tiers: Optional[List[str]] = None,
        max_items: Optional[int] = None,
    ) -> List[Dict]:
        """Filters relevant items (weapons, armor, bags, resources) by tier."""
        if not self.items:
            self.download_items_database()

        if tiers is None:
            tiers = ["T4", "T5", "T6", "T7", "T8"]

        results = []
        for it in self.items:
            uname = it.get("UniqueName", "")
            if not uname or "@" in uname:
                continue

            # Check tier match
            if any(uname.startswith(f"{t}_") for t in tiers):
                results.append(it)
                if max_items and len(results) >= max_items:
                    break

        return results

    def download_render(
        self,
        unique_name: str,
        enchantment: int = 0,
        quality: int = 1,
        force: bool = False,
    ) -> str:
        """Downloads and caches an item render icon from render.albiononline.com."""
        filename = f"{unique_name}"
        if enchantment > 0:
            filename += f"@{enchantment}"
        if quality > 1:
            filename += f"_q{quality}"
        filename += ".png"

        target_path = os.path.join(self.renders_dir, filename)
        if not force and os.path.isfile(target_path):
            return target_path

        item_slug = f"{unique_name}"
        if enchantment > 0:
            item_slug += f"@{enchantment}"

        url = f"{RENDER_BASE_URL}/{item_slug}.png"
        if quality > 1:
            url += f"?quality={quality}"

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
                with open(target_path, "wb") as f:
                    f.write(data)
            return target_path
        except Exception as e:
            return ""

    def generate_synthetic_inventory_grid(
        self,
        render_paths: List[str],
        cols: int = 4,
        rows: int = 6,
        slot_px: int = 64,
        pad_px: int = 6,
    ) -> Tuple[Image.Image, List[Tuple[int, float, float, float, float]]]:
        """
        Creates a synthetic Albion inventory grid.
        Returns:
            (PIL Image, List of YOLO labels: [class_id, x_center, y_center, width, height])
        """
        width = cols * slot_px + (cols + 1) * pad_px
        height = rows * slot_px + (rows + 1) * pad_px

        # Base background: Albion dark metal/stone UI color
        base_color = (25 + random.randint(-3, 3), 28 + random.randint(-3, 3), 34 + random.randint(-3, 3))
        canvas = Image.new("RGB", (width, height), color=base_color)
        draw = ImageDraw.Draw(canvas)

        labels = []

        for r in range(rows):
            for c in range(cols):
                x0 = pad_px + c * (slot_px + pad_px)
                y0 = pad_px + r * (slot_px + pad_px)
                x1 = x0 + slot_px
                y1 = y0 + slot_px

                # Draw slot background border (dark recessed slot)
                slot_bg = (18 + random.randint(-2, 2), 20 + random.randint(-2, 2), 24 + random.randint(-2, 2))
                draw.rectangle([x0, y0, x1, y1], fill=slot_bg, outline=(45, 48, 56), width=1)

                # Randomly leave some slots empty (25% chance)
                if random.random() < 0.25 or not render_paths:
                    continue

                render_path = random.choice(render_paths)
                try:
                    with Image.open(render_path) as icon_img:
                        icon = icon_img.convert("RGBA")
                        # Resize to fit slot with small padding
                        icon_size = slot_px - 4
                        icon_resized = icon.resize((icon_size, icon_size), Image.Resampling.BICUBIC)

                        icon_x = x0 + 2
                        icon_y = y0 + 2
                        canvas.paste(icon_resized, (icon_x, icon_y), icon_resized)

                        # Draw random stack count if stackable item
                        if random.random() < 0.4:
                            count = random.choice([2, 5, 10, 50, 100, 250, 999])
                            draw.text((x0 + 4, y1 - 16), str(count), fill=(240, 240, 240))

                        # Compute normalized YOLO bounding box
                        cx = (icon_x + icon_size / 2.0) / width
                        cy = (icon_y + icon_size / 2.0) / height
                        bw = icon_size / float(width)
                        bh = icon_size / float(height)

                        # Class 0: 'item'
                        labels.append((0, cx, cy, bw, bh))
                except Exception:
                    continue

        # Add subtle noise/blur
        np_img = np.array(canvas)
        noise = np.random.randint(-4, 4, np_img.shape, dtype=np.int16)
        np_img = np.clip(np_img.astype(np.int16) + noise, 0, 255).astype(np.uint8)

        return Image.fromarray(np_img), labels

    def export_yolo_dataset(
        self,
        render_paths: List[str],
        total_images: int = 50,
        train_ratio: float = 0.8,
    ) -> str:
        """Generates train/val image sets with YOLO annotation text files and data.yaml."""
        img_train_dir = os.path.join(self.dataset_dir, "images", "train")
        img_val_dir = os.path.join(self.dataset_dir, "images", "val")
        lbl_train_dir = os.path.join(self.dataset_dir, "labels", "train")
        lbl_val_dir = os.path.join(self.dataset_dir, "labels", "val")

        for d in [img_train_dir, img_val_dir, lbl_train_dir, lbl_val_dir]:
            os.makedirs(d, exist_ok=True)

        num_train = int(total_images * train_ratio)

        for i in range(total_images):
            img, labels = self.generate_synthetic_inventory_grid(render_paths)

            is_train = i < num_train
            target_img_dir = img_train_dir if is_train else img_val_dir
            target_lbl_dir = lbl_train_dir if is_train else lbl_val_dir

            base_name = f"albion_inv_{i:05d}"
            img.save(os.path.join(target_img_dir, f"{base_name}.jpg"), quality=95)

            with open(os.path.join(target_lbl_dir, f"{base_name}.txt"), "w", encoding="utf-8") as f:
                for cls_id, cx, cy, bw, bh in labels:
                    f.write(f"{cls_id} {cx:.6f} {cy:.6f} {bw:.6f} {bh:.6f}\n")

        # Create data.yaml
        yaml_content = f"""path: {os.path.abspath(self.dataset_dir)}
train: images/train
val: images/val

names:
  0: albion_item
"""
        yaml_path = os.path.join(self.dataset_dir, "data.yaml")
        with open(yaml_path, "w", encoding="utf-8") as f:
            f.write(yaml_content)

        return yaml_path
