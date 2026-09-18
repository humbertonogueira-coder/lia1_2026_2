#!/usr/bin/env python3
"""
Gera frames ImageFolder a partir de:
  - data/kinetics_subset/{train,val,test}/<classe>/*.mp4
  - data/custom_actions/{sitting_down,standing_up}/*.mp4  (espalhados em train/val/test)

Também pode gerar um dataset sintético mínimo de sitting_down/standing_up
para desenvolvimento quando ainda não houver clips reais (--synth-custom).
"""

from __future__ import annotations

import argparse
import random
import shutil
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SEED = 42


def extract_frames_from_video(
    video_path: Path,
    out_dir: Path,
    frames_per_video: int = 6,
) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(str(video_path))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    if total <= 0:
        cap.release()
        return 0
    idxs = np.linspace(0, total - 1, num=min(frames_per_video, total), dtype=int)
    saved = 0
    for i, fi in enumerate(idxs):
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(fi))
        ok, frame = cap.read()
        if not ok:
            continue
        out = out_dir / f"{video_path.stem}_f{i:02d}.jpg"
        cv2.imwrite(str(out), frame)
        saved += 1
    cap.release()
    return saved


def process_video_tree(video_root: Path, frames_root: Path, frames_per_video: int):
    if not video_root.exists():
        print(f"(aviso) não encontrado: {video_root}")
        return
    for split in ("train", "val", "test"):
        split_dir = video_root / split
        if not split_dir.exists():
            continue
        for class_dir in sorted(split_dir.iterdir()):
            if not class_dir.is_dir():
                continue
            out_dir = frames_root / split / class_dir.name
            videos = (
                list(class_dir.glob("*.mp4"))
                + list(class_dir.glob("*.avi"))
                + list(class_dir.glob("*.mkv"))
                + list(class_dir.glob("*.webm"))
            )
            total = 0
            for video in videos:
                total += extract_frames_from_video(video, out_dir, frames_per_video)
            print(f"{split}/{class_dir.name}: {len(videos)} vídeos → {total} frames")


def split_custom_actions(custom_root: Path, kinetics_root: Path):
    """Copia vídeos custom para train/val/test (70/15/15)."""
    random.seed(SEED)
    for class_name in ("sitting_down", "standing_up"):
        src = custom_root / class_name
        if not src.exists():
            continue
        videos = (
            list(src.glob("*.mp4"))
            + list(src.glob("*.avi"))
            + list(src.glob("*.mov"))
            + list(src.glob("*.mkv"))
        )
        if not videos:
            continue
        random.shuffle(videos)
        n = len(videos)
        n_train = max(1, int(n * 0.7))
        n_val = max(1, int(n * 0.15)) if n >= 5 else 0
        splits = {
            "train": videos[:n_train],
            "val": videos[n_train : n_train + n_val],
            "test": videos[n_train + n_val :],
        }
        if not splits["test"] and splits["train"]:
            splits["test"] = [splits["train"].pop()]
        for split_name, files in splits.items():
            dest = kinetics_root / split_name / class_name
            dest.mkdir(parents=True, exist_ok=True)
            for v in files:
                target = dest / v.name
                if not target.exists():
                    shutil.copy2(v, target)
            print(f"custom → {split_name}/{class_name}: {len(files)}")


def make_synth_custom(custom_root: Path, n_per_class: int = 20):
    """Frames sintéticos distintos para prototipar sitting_down / standing_up."""
    random.seed(SEED)
    for class_name, color, y_motion in [
        ("sitting_down", (40, 120, 220), "down"),
        ("standing_up", (40, 200, 90), "up"),
    ]:
        out = custom_root / class_name
        out.mkdir(parents=True, exist_ok=True)
        for i in range(n_per_class):
            path = out / f"synth_{class_name}_{i:02d}.mp4"
            if path.exists():
                continue
            writer = cv2.VideoWriter(
                str(path),
                cv2.VideoWriter_fourcc(*"mp4v"),
                8,
                (224, 224),
            )
            for t in range(16):
                img = np.zeros((224, 224, 3), dtype=np.uint8)
                img[:] = (30, 30, 30)
                # "chão"
                cv2.rectangle(img, (0, 170), (224, 224), (60, 60, 60), -1)
                # cadeira
                cv2.rectangle(img, (80, 120), (150, 180), (90, 90, 90), -1)
                # pessoa (círculo + corpo) sobe ou desce
                if y_motion == "down":
                    cy = 50 + int(t * 5)
                else:
                    cy = 130 - int(t * 5)
                cv2.circle(img, (115, cy), 18, color, -1)
                cv2.rectangle(img, (100, cy + 18), (130, cy + 70), color, -1)
                writer.write(img)
            writer.release()
        print(f"sintético: {class_name} → {n_per_class} vídeos em {out}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--kinetics-root",
        type=Path,
        default=ROOT / "data" / "kinetics_subset",
    )
    parser.add_argument(
        "--custom-root",
        type=Path,
        default=ROOT / "data" / "custom_actions",
    )
    parser.add_argument(
        "--frames-root",
        type=Path,
        default=ROOT / "data" / "frames",
    )
    parser.add_argument("--frames-per-video", type=int, default=6)
    parser.add_argument(
        "--synth-custom",
        action="store_true",
        help="Gera vídeos sintéticos de sitting_down/standing_up se a pasta estiver vazia",
    )
    parser.add_argument("--force-synth", action="store_true")
    args = parser.parse_args()

    custom_empty = not any(args.custom_root.rglob("*.mp4")) and not any(
        args.custom_root.rglob("*.avi")
    )
    if args.force_synth or (args.synth_custom and custom_empty):
        make_synth_custom(args.custom_root)

    split_custom_actions(args.custom_root, args.kinetics_root)

    if args.frames_root.exists():
        shutil.rmtree(args.frames_root)
    process_video_tree(args.kinetics_root, args.frames_root, args.frames_per_video)
    print(f"Frames em: {args.frames_root}")


if __name__ == "__main__":
    main()
