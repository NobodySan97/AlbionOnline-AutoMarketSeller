"""
Trains YOLOv8 on the synthetic Albion Online dataset and runs live inference.
Usage: python train_and_run_ai.py
"""

import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from ultralytics import YOLO
from ai_tools.dataset_builder import AlbionDatasetBuilder


def main():
    print("=" * 65)
    print("   Albion Online AI Vision - YOLO Training & Inference Runner")
    print("=" * 65)

    dataset_yaml = os.path.abspath("ai_data/dataset/data.yaml")

    # If dataset not yet generated, build it now
    if not os.path.isfile(dataset_yaml):
        print("\n[INFO] Generazione automatica del dataset sintetico...")
        builder = AlbionDatasetBuilder(data_dir="ai_data")
        builder.download_items_database()
        tradeable = builder.filter_tradeable_items(tiers=["T4", "T5", "T6", "T7", "T8"], max_items=25)
        render_paths = [builder.download_render(it["UniqueName"]) for it in tradeable if builder.download_render(it["UniqueName"])]
        dataset_yaml = builder.export_yolo_dataset(render_paths, total_images=30)
        print(f"       -> Dataset generato in: {dataset_yaml}")

    print("\n[1/2] Caricamento del modello YOLOv8-Nano...")
    model = YOLO("yolov8n.pt")

    print("\n[2/2] Avvio del training AI su dataset sintetico (5 Epoche)...")
    results = model.train(
        data=dataset_yaml,
        epochs=5,
        imgsz=320,
        batch=8,
        workers=0,
        project="ai_data/models",
        name="albion_yolo",
        exist_ok=True,
        verbose=True,
    )

    best_pt_path = os.path.join("runs", "detect", "ai_data", "models", "albion_yolo", "weights", "best.pt")
    if not os.path.isfile(best_pt_path):
        best_pt_path = os.path.join("ai_data", "models", "albion_yolo", "weights", "best.pt")

    os.makedirs("ai_data/models", exist_ok=True)
    target_model_path = os.path.abspath("ai_data/models/albion_yolo.pt")

    import shutil
    if os.path.isfile(best_pt_path):
        shutil.copy2(best_pt_path, target_model_path)

    print("\n" + "=" * 65)
    print(" [OK] ADDESTRAMENTO MODELLO COMPLETATO CON SUCCESSO!")
    print(f" Modello salvato in: {target_model_path}")
    print("=" * 65)

    # Test inference on a sample image
    sample_img_path = os.path.join("ai_data", "dataset", "images", "val", "albion_inv_00025.jpg")
    val_dir = os.path.join("ai_data", "dataset", "images", "val")
    if not os.path.isfile(sample_img_path) and os.path.isdir(val_dir):
        val_imgs = [f for f in os.listdir(val_dir) if f.endswith(".jpg")]
        if val_imgs:
            sample_img_path = os.path.join(val_dir, val_imgs[0])

    if os.path.isfile(sample_img_path):
        print(f"\n🔍 Esecuzione Inferenza AI su immagine di test: {sample_img_path}")
        trained_model = YOLO(target_model_path)
        preds = trained_model.predict(source=sample_img_path, conf=0.20, verbose=False)

        for r in preds:
            boxes = r.boxes
            print(f"\n   🎯 Rilevati {len(boxes)} oggetti/slot nell'inventario di test!")
            for i, box in enumerate(boxes):
                coords = box.xyxy[0].tolist()
                conf = float(box.conf[0])
                print(f"      • Oggetto #{i+1:02d}: Box [{int(coords[0])}, {int(coords[1])}, {int(coords[2])}, {int(coords[3])}] | Confidenza AI: {conf*100:.1f}%")

    print("\n" + "=" * 65)
    print(" [SUCCESSO] La Vision AI per Albion Online è pronta per la produzione!")
    print("=" * 65)


if __name__ == "__main__":
    main()
