#!/usr/bin/env python3
"""Treina CNN Residual no subset Kinetics/custom e exporta ONNX."""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
from sklearn.metrics import classification_report
from torch.utils.data import DataLoader
from torchvision import transforms
from torchvision.datasets import ImageFolder
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))
from model_arch import CNNResidual  # noqa: E402

SEED = 42
IMG_SIZE = 128
BATCH_SIZE = 32
MEAN = [0.485, 0.456, 0.406]
STD = [0.229, 0.224, 0.225]


def set_seed(seed: int = SEED) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def extract_frames(
    video_root: Path,
    frames_root: Path,
    frames_per_video: int = 8,
) -> None:
    """Converte vídeos em pastas ImageFolder: split/classe/*.jpg"""
    for split in ("train", "val", "test"):
        split_in = video_root / split
        if not split_in.exists():
            continue
        for class_dir in sorted(split_in.iterdir()):
            if not class_dir.is_dir():
                continue
            out_dir = frames_root / split / class_dir.name
            out_dir.mkdir(parents=True, exist_ok=True)
            videos = sorted(
                list(class_dir.glob("*.avi"))
                + list(class_dir.glob("*.mp4"))
                + list(class_dir.glob("*.mkv"))
            )
            for video in videos:
                cap = cv2.VideoCapture(str(video))
                total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
                if total <= 0:
                    cap.release()
                    continue
                indices = np.linspace(
                    0, max(total - 1, 0), num=min(frames_per_video, total), dtype=int
                )
                for i, frame_idx in enumerate(indices):
                    cap.set(cv2.CAP_PROP_POS_FRAMES, int(frame_idx))
                    ok, frame = cap.read()
                    if not ok:
                        continue
                    out = out_dir / f"{video.stem}_f{i:02d}.jpg"
                    cv2.imwrite(str(out), frame)
                cap.release()


def build_loaders(frames_root: Path):
    transform_train = transforms.Compose(
        [
            transforms.Resize((int(IMG_SIZE * 1.15), int(IMG_SIZE * 1.15))),
            transforms.RandomCrop(IMG_SIZE),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(12),
            transforms.ColorJitter(0.2, 0.2, 0.2),
            transforms.ToTensor(),
            transforms.Normalize(MEAN, STD),
        ]
    )
    transform_eval = transforms.Compose(
        [
            transforms.Resize((IMG_SIZE, IMG_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(MEAN, STD),
        ]
    )

    ds_train = ImageFolder(frames_root / "train", transform=transform_train)
    ds_val = ImageFolder(frames_root / "val", transform=transform_eval)
    ds_test = ImageFolder(frames_root / "test", transform=transform_eval)

    loader_train = DataLoader(ds_train, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
    loader_val = DataLoader(ds_val, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)
    loader_test = DataLoader(ds_test, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)
    return ds_train, loader_train, loader_val, loader_test


def train_one_epoch(model, loader, optim, criterion, device):
    model.train()
    loss_total = correct = total = 0
    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)
        optim.zero_grad()
        logits = model(images)
        loss = criterion(logits, labels)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optim.step()
        loss_total += loss.item() * images.size(0)
        correct += (logits.argmax(1) == labels).sum().item()
        total += images.size(0)
    return loss_total / total, 100 * correct / total


@torch.no_grad()
def evaluate(model, loader, criterion, device):
    model.eval()
    loss_total = correct = total = 0
    all_preds, all_labels = [], []
    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)
        logits = model(images)
        loss = criterion(logits, labels)
        preds = logits.argmax(1)
        loss_total += loss.item() * images.size(0)
        correct += (preds == labels).sum().item()
        total += images.size(0)
        all_preds.append(preds.cpu())
        all_labels.append(labels.cpu())
    preds_np = torch.cat(all_preds).numpy()
    labels_np = torch.cat(all_labels).numpy()
    return loss_total / total, 100 * correct / total, preds_np, labels_np


def export_onnx(model, classes, out_path: Path, device):
    import onnx

    model.eval()
    dummy = torch.randn(1, 3, IMG_SIZE, IMG_SIZE, device=device)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    torch.onnx.export(
        model,
        dummy,
        str(out_path),
        input_names=["imagem"],
        output_names=["predicoes"],
        opset_version=18,
        dynamo=False,
    )
    model_onnx = onnx.load(str(out_path))
    meta = {
        "task": "action_recognition_frame",
        "classes": json.dumps(classes),
        "img_size": str(IMG_SIZE),
        "mean": json.dumps(MEAN),
        "std": json.dumps(STD),
        "color_mode": "RGB",
        "framework": "PyTorch",
        "architecture": "CNNResidual",
        "dataset": "kinetics_subset_classroom",
    }
    for k, v in meta.items():
        prop = model_onnx.metadata_props.add()
        prop.key = k
        prop.value = v
    onnx.save(model_onnx, str(out_path))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--video-root",
        type=Path,
        default=ROOT / "data" / "kinetics_subset",
    )
    parser.add_argument(
        "--frames-root",
        type=Path,
        default=ROOT / "data" / "frames",
    )
    parser.add_argument("--epochs", type=int, default=12)
    parser.add_argument("--patience", type=int, default=4)
    parser.add_argument("--frames-per-video", type=int, default=6)
    parser.add_argument(
        "--onnx-out",
        type=Path,
        default=ROOT / "models" / "narrador_cenas.onnx",
    )
    parser.add_argument("--skip-extract", action="store_true")
    args = parser.parse_args()

    set_seed()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    if not args.skip_extract or not (args.frames_root / "train").exists():
        print("Extraindo frames...")
        extract_frames(args.video_root, args.frames_root, args.frames_per_video)

    ds_train, loader_train, loader_val, loader_test = build_loaders(args.frames_root)
    classes = ds_train.classes
    print(f"Classes ({len(classes)}): {classes}")
    print(f"Treino: {len(ds_train)} frames")

    model = CNNResidual(n_classes=len(classes), dropout=0.3).to(device)
    optim = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=1e-4)
    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)

    ckpt = ROOT / "models" / "melhor_modelo.pth"
    ckpt.parent.mkdir(parents=True, exist_ok=True)
    best_val = float("inf")
    stale = 0

    for epoch in range(1, args.epochs + 1):
        tr_loss, tr_acc = train_one_epoch(model, loader_train, optim, criterion, device)
        va_loss, va_acc, _, _ = evaluate(model, loader_val, criterion, device)
        mark = ""
        if va_loss < best_val:
            best_val = va_loss
            stale = 0
            torch.save(model.state_dict(), ckpt)
            mark = "*"
        else:
            stale += 1
        print(
            f"Epoch {epoch:02d} | train {tr_loss:.4f}/{tr_acc:.1f}% | "
            f"val {va_loss:.4f}/{va_acc:.1f}% {mark}"
        )
        if stale >= args.patience:
            print("Early stopping")
            break

    model.load_state_dict(torch.load(ckpt, map_location=device, weights_only=True))
    te_loss, te_acc, preds, labels = evaluate(model, loader_test, criterion, device)
    print(f"\nTeste: loss={te_loss:.4f} acc={te_acc:.2f}%")
    print(classification_report(labels, preds, target_names=classes, zero_division=0))

    export_onnx(model, classes, args.onnx_out, device)
    print(f"ONNX salvo em {args.onnx_out} ({args.onnx_out.stat().st_size / 1e6:.2f} MB)")

    # Copia um vídeo de exemplo por classe para sample_data
    sample_dir = ROOT / "sample_data"
    sample_dir.mkdir(exist_ok=True)
    for class_dir in sorted((args.video_root / "test").iterdir()):
        if not class_dir.is_dir():
            continue
        vids = (
            list(class_dir.glob("*.mp4"))
            + list(class_dir.glob("*.avi"))
            + list(class_dir.glob("*.webm"))
        )
        if vids:
            dest = sample_dir / f"{class_dir.name}{vids[0].suffix}"
            dest.write_bytes(vids[0].read_bytes())
    print(f"Exemplos em {sample_dir}")


if __name__ == "__main__":
    main()
