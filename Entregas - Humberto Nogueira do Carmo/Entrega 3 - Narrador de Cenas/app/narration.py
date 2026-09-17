"""Templates de narração em português a partir das classes UCF-101."""

from __future__ import annotations

from collections import Counter
from typing import Iterable

NARRATION_TEMPLATES: dict[str, str] = {
    "ApplyEyeMakeup": "Na cena, alguém está aplicando maquiagem nos olhos.",
    "ApplyLipstick": "Na cena, alguém está passando batom.",
    "Archery": "Na cena, uma pessoa está praticando arco e flecha.",
    "BabyCrawling": "Na cena, um bebê está engatinhando.",
    "BalanceBeam": "Na cena, uma ginasta está se equilibrando na trave.",
    "BandMarching": "Na cena, uma banda está marchando em formação.",
    "BaseballPitch": "Na cena, um jogador está arremessando no beisebol.",
    "Basketball": "Na cena, alguém está jogando basquete.",
    "BasketballDunk": "Na cena, um jogador está enterrando a bola no basquete.",
    "BenchPress": "Na cena, alguém está fazendo exercício de supino.",
}

CLASS_LABELS_PT: dict[str, str] = {
    "ApplyEyeMakeup": "maquiagem nos olhos",
    "ApplyLipstick": "passar batom",
    "Archery": "arco e flecha",
    "BabyCrawling": "bebê engatinhando",
    "BalanceBeam": "trave de equilíbrio",
    "BandMarching": "banda marchando",
    "BaseballPitch": "arremesso de beisebol",
    "Basketball": "basquete",
    "BasketballDunk": "enterrada no basquete",
    "BenchPress": "supino",
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
    """Gera um parágrafo narrativo a partir de previsões frame a frame."""
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

    # Mudanças ao longo do tempo (simplificado)
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
