"""
Session stats tracking and CSV export with bounded memory usage.
"""

from collections import deque
import csv
import datetime
import threading
import time


class SessionStats:
    MAX_IN_MEMORY_RECORDS = 2000  # Cap in-memory history to prevent unbounded heap growth

    def __init__(self):
        self.start_time = time.time()
        self.total_orders = 0
        self.total_silver = 0
        self.records = deque(maxlen=self.MAX_IN_MEMORY_RECORDS)
        self.lock = threading.Lock()

    @property
    def orders(self):
        """Backward-compatibility alias pointing directly to self.records without duplicating memory."""
        return self.records

    def record_sale(
        self, price: int = 0, strategy: str = "normal", reason: str = "ok", diff_percent: float = 0.0, item_name: str = "Item"
    ):
        with self.lock:
            self.total_orders += 1
            self.total_silver += price
            rec = {
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "item": item_name,
                "price": price,
                "strategy": strategy,
                "reason": reason,
                "diff_percent": round(diff_percent, 2),
            }
            self.records.append(rec)

    def reset(self):
        with self.lock:
            self.total_orders = 0
            self.total_silver = 0
            self.start_time = time.time()
            self.records.clear()

    @property
    def average_price(self) -> int:
        with self.lock:
            return int(round(self.total_silver / self.total_orders)) if self.total_orders > 0 else 0

    @property
    def elapsed_formatted(self) -> str:
        s = int(time.time() - self.start_time)
        return f"{s // 3600:02d}:{(s % 3600) // 60:02d}:{s % 60:02d}"

    def export_csv(self, filepath: str):
        with self.lock:
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(
                    f, fieldnames=["timestamp", "item", "price", "strategy", "reason", "diff_percent"]
                )
                writer.writeheader()
                writer.writerows(list(self.records))
