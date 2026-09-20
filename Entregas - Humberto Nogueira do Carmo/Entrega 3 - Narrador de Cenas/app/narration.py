"""Templates de narração em português — Kinetics (porta/andar) + ações de sala."""

from __future__ import annotations

from collections import Counter
from typing import Iterable

NARRATION_TEMPLATES: dict[str, str] = {
    "opening_door": "Na cena, alguém está abrindo a porta.",
    "closing_door": "Na cena, alguém está fechando a porta.",
    "walking": "Na cena, uma pessoa está andando.",
    "clapping": "Na cena, alguém está batendo palmas.",
    "stretching_arm": "Na cena, alguém está alongando o braço.",
    "pushing_cart": "Na cena, alguém está empurrando um carrinho.",
    "standing_up": "Na cena, uma pessoa está se levantando da cadeira.",
    "sitting_down": "Na cena, uma pessoa está se sentando.",
}

CLASS_LABELS_PT: dict[str, str] = {
    "opening_door": "abrindo a porta",
    "closing_door": "fechando a porta",
    "walking": "andando",
    "clapping": "batendo palmas",
    "stretching_arm": "alongando o braço",
    "pushing_cart": "empurrando carrinho",
    "standing_up": "levantando da cadeira",
    "sitting_down": "sentando",
}


def narrate_action(class_name: str, confidence: float | None = None) -> str:
    text = NARRATION_TEMPLATES.get(
        class_name,
        f"Na cena, a ação detectada é: {class_name}.",
    )
    if confidence is not None:
        text = f"{text} (confiança: {confidence:.0%})"
    return text


def summarize_timeline(
    predictions: Iterable[dict],
    min_confidence: float = 0.35,
) -> str:
    filtered = [
        p for p in predictions if float(p.get("confidence", 0)) >= min_confidence
    ]
    if not filtered:
        return "Não foi possível identificar com confiança o que acontece na cena."

    counts = Counter(p["class"] for p in filtered)
    dominant, _ = counts.most_common(1)[0]
    avg_conf = sum(p["confidence"] for p in filtered if p["class"] == dominant) / max(
        1, counts[dominant]
    )

    parts = [narrate_action(dominant, avg_conf)]

    secondary = [c for c, _ in counts.most_common(3) if c != dominant]
    if secondary:
        labels = ", ".join(CLASS_LABELS_PT.get(c, c) for c in secondary)
        parts.append(f"Também aparecem trechos com: {labels}.")

    changes: list[str] = []
    last = None
    for p in filtered:
        if p["class"] != last:
            t = p.get("timestamp_sec")
            label = CLASS_LABELS_PT.get(p["class"], p["class"])
            if t is not None:
                changes.append(f"em {t:.1f}s → {label}")
            last = p["class"]
    if len(changes) > 1:
        parts.append("Linha do tempo: " + "; ".join(changes[:8]) + ".")

    return " ".join(parts)
