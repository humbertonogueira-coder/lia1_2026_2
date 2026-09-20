#!/usr/bin/env python3
"""
Baixa subset de ações para a demo de sala a partir do Kinetics-700-2020
(anotações oficiais). Usamos K700 porque 'opening door' / 'closing door'
NÃO existem no Kinetics-400.

Classes baixadas (pasta local):
  opening door -> opening_door
  closing door -> closing_door
  walking the dog -> walking
  clapping -> clapping
  stretching arm -> stretching_arm
  pushing cart -> pushing_cart

sitting_down / standing_up: ver scripts/prepare_custom_actions.md
"""

from __future__ import annotations

import argparse
import csv
import random
import shutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from urllib.request import urlretrieve

ROOT = Path(__file__).resolve().parents[1]
SEED = 42

CLASS_MAP = {
    "opening door": "opening_door",
    "closing door": "closing_door",
    "walking the dog": "walking",
    "clapping": "clapping",
    "stretching arm": "stretching_arm",
    "pushing cart": "pushing_cart",
}

ANNOT_URLS = {
    "train": "https://s3.amazonaws.com/kinetics/700_2020/annotations/train.csv",
    "val": "https://s3.amazonaws.com/kinetics/700_2020/annotations/val.csv",
}


def yt_dlp_argv() -> list[str]:
    local = ROOT / ".venv" / "bin" / "yt-dlp"
    if local.exists():
        return [str(local)]
    which = shutil.which("yt-dlp")
    if which:
        return [which]
    return [sys.executable, "-m", "yt_dlp"]


def download_annotations(out_dir: Path) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {}
    for split, url in ANNOT_URLS.items():
        dest = out_dir / f"k700_{split}.csv"
        if not dest.exists() or dest.stat().st_size < 1000:
            print(f"Baixando anotações {split}...")
            urlretrieve(url, dest)
        paths[split] = dest
    return paths


def load_rows(csv_path: Path, labels: set[str]) -> dict[str, list[dict]]:
    by_label: dict[str, list[dict]] = defaultdict(list)
    with csv_path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            label = (row.get("label") or "").strip()
            if label in labels:
                by_label[label].append(row)
    return by_label


def download_clip(
    url: str,
    out_path: Path,
    start: float,
    end: float,
) -> Path | None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    existing = list(out_path.parent.glob(out_path.stem + ".*"))
    for e in existing:
        if e.stat().st_size > 10_000:
            return e

    tmpl = str(out_path.with_suffix("")) + ".%(ext)s"
    cmd = yt_dlp_argv() + [
        "--no-playlist",
        "-f",
        "mp4/best[height<=360]/best",
        "-o",
        tmpl,
        "--quiet",
        "--no-warnings",
        "--download-sections",
        f"*{start}-{end}",
        "--force-keyframes-at-cuts",
        url,
    ]
    try:
        subprocess.run(cmd, check=True, timeout=180)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return None

    matches = sorted(
        out_path.parent.glob(out_path.stem + ".*"),
        key=lambda p: p.stat().st_size,
        reverse=True,
    )
    for m in matches:
        if m.suffix.lower() in {".mp4", ".webm", ".mkv"} and m.stat().st_size > 10_000:
            return m
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=ROOT / "data" / "kinetics_subset")
    parser.add_argument(
        "--annot-dir", type=Path, default=ROOT / "data" / "kinetics_annotations"
    )
    parser.add_argument("--per-class-train", type=int, default=10)
    parser.add_argument("--per-class-val", type=int, default=2)
    parser.add_argument("--per-class-test", type=int, default=2)
    args = parser.parse_args()

    random.seed(SEED)
    annot = download_annotations(args.annot_dir)
    labels = set(CLASS_MAP.keys())
    train_rows = load_rows(annot["train"], labels)
    val_rows = load_rows(annot["val"], labels)

    pools: dict[str, list[dict]] = {}
    for label in labels:
        pools[label] = train_rows.get(label, []) + val_rows.get(label, [])
        print(f"{label}: {len(pools[label])} anotações")

    args.out_dir.mkdir(parents=True, exist_ok=True)

    for label, folder in CLASS_MAP.items():
        pool = list(pools[label])
        random.shuffle(pool)
        want = args.per_class_train + args.per_class_val + args.per_class_test
        downloaded: list[Path] = []

        for row in pool:
            if len(downloaded) >= want:
                break
            vid = (row.get("youtube_id") or "").strip()
            if not vid:
                continue
            try:
                start = float(row["time_start"])
                end = float(row["time_end"])
            except (KeyError, ValueError):
                continue
            url = f"https://www.youtube.com/watch?v={vid}"
            dest = args.out_dir / "_raw" / folder / f"{vid}.mp4"
            found = download_clip(url, dest, start, end)
            if found:
                downloaded.append(found)
                print(f"  OK {folder}: {found.name}")

        random.shuffle(downloaded)
        splits = {
            "train": downloaded[: args.per_class_train],
            "val": downloaded[
                args.per_class_train : args.per_class_train + args.per_class_val
            ],
            "test": downloaded[
                args.per_class_train
                + args.per_class_val : args.per_class_train
                + args.per_class_val
                + args.per_class_test
            ],
        }
        for split_name, files in splits.items():
            out_c = args.out_dir / split_name / folder
            out_c.mkdir(parents=True, exist_ok=True)
            for src in files:
                target = out_c / src.name
                if not target.exists():
                    shutil.copy2(src, target)
            print(f"  → {split_name}/{folder}: {len(files)}")

    print(f"\nConcluído: {args.out_dir}")
    print("Se poucas classes baixaram (YouTube bloqueado), use:")
    print("  python scripts/generate_demo_dataset.py")


if __name__ == "__main__":
    main()
