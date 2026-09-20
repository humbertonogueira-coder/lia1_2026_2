"""Inferência ONNX sobre frames de vídeo + narração."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import onnxruntime as ort
from PIL import Image

DEFAULT_MEAN = [0.485, 0.456, 0.406]
DEFAULT_STD = [0.229, 0.224, 0.225]


def load_onnx_model(model_path: str | Path) -> tuple[ort.InferenceSession, dict[str, Any]]:
    path = Path(model_path)
    if not path.exists():
        raise FileNotFoundError(f"Modelo ONNX não encontrado: {path}")

    session = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
    meta = dict(session.get_modelmeta().custom_metadata_map)

    classes = json.loads(meta.get("classes", "[]"))
    img_size = int(meta.get("img_size", "128"))
    mean = json.loads(meta.get("mean", json.dumps(DEFAULT_MEAN)))
    std = json.loads(meta.get("std", json.dumps(DEFAULT_STD)))

    return session, {
        "classes": classes,
        "img_size": img_size,
        "mean": mean,
        "std": std,
        "input_name": session.get_inputs()[0].name,
        "output_name": session.get_outputs()[0].name,
    }


def preprocess_frame(
    frame_bgr: np.ndarray,
    img_size: int,
    mean: list[float],
    std: list[float],
) -> np.ndarray:
    rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(rgb).resize((img_size, img_size))
    arr = np.asarray(img).astype(np.float32) / 255.0
    arr = (arr - np.array(mean, dtype=np.float32)) / np.array(std, dtype=np.float32)
    arr = np.transpose(arr, (2, 0, 1))[None, ...]  # NCHW
    return arr.astype(np.float32)


def softmax(logits: np.ndarray) -> np.ndarray:
    x = logits - np.max(logits, axis=-1, keepdims=True)
    e = np.exp(x)
    return e / np.sum(e, axis=-1, keepdims=True)


def predict_frame(
    session: ort.InferenceSession,
    cfg: dict[str, Any],
    frame_bgr: np.ndarray,
) -> dict[str, Any]:
    tensor = preprocess_frame(frame_bgr, cfg["img_size"], cfg["mean"], cfg["std"])
    logits = session.run([cfg["output_name"]], {cfg["input_name"]: tensor})[0]
    probs = softmax(logits)[0]
    idx = int(np.argmax(probs))
    return {
        "class": cfg["classes"][idx],
        "confidence": float(probs[idx]),
        "probabilities": {
            cfg["classes"][i]: float(probs[i]) for i in range(len(cfg["classes"]))
        },
    }


def sample_video_frames(
    video_path: str | Path,
    every_n_frames: int = 15,
    max_frames: int = 40,
) -> list[tuple[float, np.ndarray]]:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Não foi possível abrir o vídeo: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    frames: list[tuple[float, np.ndarray]] = []
    idx = 0

    while len(frames) < max_frames:
        ok, frame = cap.read()
        if not ok:
            break
        if idx % every_n_frames == 0:
            ts = idx / fps
            frames.append((ts, frame))
        idx += 1

    cap.release()
    return frames


def narrate_image(
    image_bgr: np.ndarray,
    model_path: str | Path,
) -> dict[str, Any]:
    """Classifica um único frame (ex.: captura da webcam)."""
    from narration import narrate_action

    session, cfg = load_onnx_model(model_path)
    pred = predict_frame(session, cfg, image_bgr)
    pred["caption"] = narrate_action(pred["class"], pred["confidence"])
    pred["summary"] = pred["caption"]
    return pred


def narrate_video(
    video_path: str | Path,
    model_path: str | Path,
    every_n_frames: int = 15,
    max_frames: int = 40,
    min_confidence: float = 0.35,
) -> dict[str, Any]:
    from narration import summarize_timeline, narrate_action

    session, cfg = load_onnx_model(model_path)
    sampled = sample_video_frames(video_path, every_n_frames, max_frames)

    predictions: list[dict[str, Any]] = []
    for ts, frame in sampled:
        pred = predict_frame(session, cfg, frame)
        pred["timestamp_sec"] = ts
        pred["caption"] = narrate_action(pred["class"], pred["confidence"])
        predictions.append(pred)

    return {
        "summary": summarize_timeline(predictions, min_confidence=min_confidence),
        "predictions": predictions,
        "num_frames": len(predictions),
        "classes": cfg["classes"],
    }
