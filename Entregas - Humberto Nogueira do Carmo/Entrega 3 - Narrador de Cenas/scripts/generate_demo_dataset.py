#!/usr/bin/env python3
"""
Gera um dataset demo sintético das 8 classes (para treino local / CI)
quando o download do YouTube (Kinetics) não estiver disponível.
Visualmente distinto por classe — útil para validar o pipeline ONNX/webcam.
Substitua por Kinetics real + clips custom antes da aula.
"""

from __future__ import annotations

import argparse
import random
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SEED = 42

CLASSES = [
    ("opening_door", (0, 140, 255), "door_open"),
    ("closing_door", (0, 90, 200), "door_close"),
    ("walking", (50, 200, 50), "walk"),
    ("clapping", (220, 80, 80), "clap"),
    ("stretching_arm", (200, 180, 40), "stretch"),
    ("pushing_cart", (160, 60, 200), "push"),
    ("standing_up", (40, 200, 90), "stand"),
    ("sitting_down", (40, 120, 220), "sit"),
]


def draw_scene(class_key: str, t: int, color) -> np.ndarray:
    img = np.zeros((224, 224, 3), dtype=np.uint8)
    img[:] = (28, 28, 32)
    cv2.rectangle(img, (0, 175), (224, 224), (55, 55, 55), -1)

    if class_key.startswith("door"):
        # porta na direita
        door_x = 150 + (int(t * 3) if class_key == "door_open" else 40 - int(t * 3))
        door_x = max(120, min(190, door_x))
        cv2.rectangle(img, (140, 40), (200, 180), (70, 50, 40), -1)
        cv2.rectangle(img, (door_x, 40), (door_x + 45, 180), color, -1)
        cv2.circle(img, (90, 90 + (t % 3)), 14, (230, 200, 180), -1)
    elif class_key == "walk":
        x = 20 + t * 10
        cv2.circle(img, (x, 90), 14, color, -1)
        cv2.rectangle(img, (x - 10, 104), (x + 10, 160), color, -1)
    elif class_key == "clap":
        cx = 112
        off = 20 - abs(8 - (t % 16))
        cv2.circle(img, (cx, 70), 14, (230, 200, 180), -1)
        cv2.rectangle(img, (cx - 12, 84), (cx + 12, 150), (200, 180, 160), -1)
        cv2.circle(img, (cx - 25 - off, 100), 10, color, -1)
        cv2.circle(img, (cx + 25 + off, 100), 10, color, -1)
    elif class_key == "stretch":
        cv2.circle(img, (112, 80), 14, (230, 200, 180), -1)
        cv2.rectangle(img, (100, 94), (124, 150), (200, 180, 160), -1)
        arm_y = 90 - t * 3
        cv2.line(img, (124, 110), (180, arm_y), color, 6)
    elif class_key == "push":
        x = 30 + t * 8
        cv2.rectangle(img, (x, 120), (x + 50, 160), (100, 100, 100), -1)
        cv2.circle(img, (x - 15, 90), 12, color, -1)
        cv2.rectangle(img, (x - 25, 102), (x - 5, 155), color, -1)
    elif class_key == "stand":
        cy = 130 - t * 5
        cv2.rectangle(img, (80, 120), (150, 180), (90, 90, 90), -1)
        cv2.circle(img, (115, cy), 16, color, -1)
        cv2.rectangle(img, (100, cy + 16), (130, cy + 65), color, -1)
    else:  # sit
        cy = 50 + t * 5
        cv2.rectangle(img, (80, 120), (150, 180), (90, 90, 90), -1)
        cv2.circle(img, (115, cy), 16, color, -1)
        cv2.rectangle(img, (100, cy + 16), (130, cy + 65), color, -1)
    return img


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=ROOT / "data" / "kinetics_subset")
    parser.add_argument("--train", type=int, default=16)
    parser.add_argument("--val", type=int, default=4)
    parser.add_argument("--test", type=int, default=4)
    args = parser.parse_args()
    random.seed(SEED)

    for folder, color, key in CLASSES:
        counts = {"train": args.train, "val": args.val, "test": args.test}
        idx = 0
        for split, n in counts.items():
            out = args.out_dir / split / folder
            out.mkdir(parents=True, exist_ok=True)
            for i in range(n):
                path = out / f"demo_{folder}_{idx:03d}.mp4"
                idx += 1
                if path.exists():
                    continue
                writer = cv2.VideoWriter(
                    str(path), cv2.VideoWriter_fourcc(*"mp4v"), 8, (224, 224)
                )
                phase = random.randint(0, 3)
                for t in range(16):
                    writer.write(draw_scene(key, t + phase, color))
                writer.release()
        print(f"{folder}: train={args.train} val={args.val} test={args.test}")

    print(f"Dataset demo em {args.out_dir}")
    print("AVISO: sintético — para a aula rode download_kinetics_subset.py + clips custom.")


if __name__ == "__main__":
    main()
