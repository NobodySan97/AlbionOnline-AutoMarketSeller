"""
Interactive CLI for Albion Online AI Dataset Generation & Vision Tools
Usage: python run_ai_generator.py
"""

import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from ai_tools.dataset_builder import AlbionDatasetBuilder


def main():
    print("=" * 65)
    print("   Albion Online AI Vision - Dataset Generator & Toolkit")
    print("=" * 65)

    builder = AlbionDatasetBuilder(data_dir="ai_data")

    print("\n[1/3] Scaricamento del database oggetti da ao-bin-dumps...")
    items = builder.download_items_database()
    print(f"      -> {len(items)} oggetti caricati nel database.")

    print("\n[2/3] Download dei render ufficiali per equipaggiamento (T4-T8)...")
    tradeable = builder.filter_tradeable_items(tiers=["T4", "T5", "T6", "T7", "T8"], max_items=25)
    print(f"      -> Selezionati {len(tradeable)} oggetti chiave per il training.")

    render_paths = []
    for it in tradeable:
        uname = it.get("UniqueName")
        p = builder.download_render(uname)
        if p and os.path.isfile(p):
            render_paths.append(p)

    print(f"      -> {len(render_paths)} icone HD scaricate da render.albiononline.com.")

    print("\n[3/3] Generazione Dataset Sintetico YOLO (Immagini + Labels)...")
    yaml_path = builder.export_yolo_dataset(render_paths, total_images=30)
    print(f"      -> Dataset generato con successo in: {os.path.abspath('ai_data/dataset')}")
    print(f"      -> File di configurazione YOLO: {yaml_path}")

    print("\n" + "=" * 65)
    print(" [OK] DATASET AI PRONTO PER L'ADDESTRAMENTO!")
    print(" Per avviare il training di YOLOv8 su questo dataset ti basta eseguire:")
    print("   pip install ultralytics")
    print(f"   yolo detect train data={yaml_path} model=yolov8n.pt epochs=30 imgsz=640")
    print("=" * 65)


if __name__ == "__main__":
    main()
