#!/usr/bin/env python3
"""Baixa o subset UCF-101 (SayakPaul/ucf101-subset) do Hugging Face."""

from __future__ import annotations

import argparse
import tarfile
from pathlib import Path

from huggingface_hub import hf_hub_download

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=ROOT / "data")
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    archive = hf_hub_download(
        repo_id="SayakPaul/ucf101-subset",
        repo_type="dataset",
        filename="UCF101_subset.tar.gz",
        local_dir=str(args.out_dir),
    )
    print(f"Arquivo: {archive}")

    extract_to = args.out_dir
    # O arquivo é tar POSIX (mesmo com extensão .tar.gz)
    with tarfile.open(archive, "r:*") as tar:
        tar.extractall(path=extract_to)

    subset = extract_to / "UCF101_subset"
    print(f"Extraído em: {subset}")
    if subset.exists():
        n = sum(1 for _ in subset.rglob("*.avi"))
        print(f"Vídeos .avi: {n}")


if __name__ == "__main__":
    main()
