"""
Narrador de Cenas — Streamlit
Modos: arquivo de vídeo OU webcam → ONNX → narração (+ Telegram broadcast)
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import cv2
import numpy as np
import streamlit as st
from dotenv import load_dotenv

APP_DIR = Path(__file__).resolve().parent
ROOT = APP_DIR.parent
sys.path.insert(0, str(APP_DIR))

load_dotenv(ROOT / ".env")

from inference import narrate_image, narrate_video  # noqa: E402
from telegram_notify import TelegramNotifier  # noqa: E402

DEFAULT_MODEL = ROOT / "models" / "narrador_cenas.onnx"

st.set_page_config(
    page_title="Narrador de Cenas",
    page_icon="🎬",
    layout="centered",
)

st.title("Narrador de Cenas")
st.caption(
    "Ações de sala (porta, andar, levantar, palmas) via ONNX — arquivo ou webcam."
)

with st.sidebar:
    st.header("Configuração")
    model_path = st.text_input("Caminho do modelo ONNX", value=str(DEFAULT_MODEL))
    every_n = st.slider("Amostrar 1 frame a cada N (vídeo)", 5, 60, 15)
    max_frames = st.slider("Máximo de frames (vídeo)", 5, 80, 30)
    min_conf = st.slider("Confiança mínima", 0.1, 0.9, 0.35, 0.05)

    st.divider()
    st.subheader("Monitoramento Telegram")
    st.caption(
        "Token no `.env` (`TELEGRAM_BOT_TOKEN`). "
        "Usuários cadastrados com /start recebem o broadcast. "
        "Para AO VIVO contínuo use `iniciar_narrador.bat` / `Narrar.py`."
    )
    monitoring = st.toggle("Ativar monitoramento", value=False)
    bot_token = st.text_input(
        "Bot token",
        value=os.getenv("TELEGRAM_BOT_TOKEN", ""),
        type="password",
    )
    notifier_preview = TelegramNotifier(bot_token=bot_token)
    n_subs = len(notifier_preview.list_subscribers()) if bot_token else 0
    st.write(f"Cadastrados: **{n_subs}**")

mode = st.radio(
    "Fonte da cena",
    options=["Arquivo de vídeo", "Webcam"],
    horizontal=True,
)


def maybe_telegram(summary: str, name: str) -> None:
    if not monitoring:
        return
    notifier = TelegramNotifier(bot_token=bot_token)
    if not notifier.configured:
        st.warning("Monitoramento ligado, mas TELEGRAM_BOT_TOKEN está vazio no .env.")
        return
    if not notifier.list_subscribers():
        st.warning(
            "Nenhum usuário cadastrado. Peça /start no bot (teclado AO VIVO | PARAR)."
        )
        return
    try:
        results = notifier.send_scene_alert(summary, video_name=name)
        ok = sum(1 for r in results if r.get("ok") is not False and "error" not in r)
        st.info(f"Aviso enviado ao Telegram ({ok}/{len(results)} cadastrados).")
    except Exception as exc:  # noqa: BLE001
        st.error(f"Falha ao enviar ao Telegram: {exc}")


if mode == "Arquivo de vídeo":
    uploaded = st.file_uploader(
        "Envie um vídeo (.avi, .mp4, .mov, .mkv)",
        type=["avi", "mp4", "mov", "mkv"],
    )
    sample_dir = ROOT / "sample_data"
    sample_videos = sorted(sample_dir.glob("*.mp4")) + sorted(sample_dir.glob("*.avi"))
    sample_choice = None
    if sample_videos:
        sample_choice = st.selectbox(
            "Ou use um vídeo de exemplo",
            options=["(nenhum)"] + [p.name for p in sample_videos],
        )

    if st.button("Narrar cena", type="primary", use_container_width=True):
        video_path = None
        video_name = ""
        tmp_path = None
        try:
            if uploaded is not None:
                suffix = Path(uploaded.name).suffix or ".mp4"
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                tmp.write(uploaded.read())
                tmp.close()
                tmp_path = tmp.name
                video_path = tmp_path
                video_name = uploaded.name
            elif sample_choice and sample_choice != "(nenhum)":
                video_path = str(sample_dir / sample_choice)
                video_name = sample_choice
            else:
                st.warning("Envie um vídeo ou escolha um exemplo.")
                st.stop()

            if not Path(model_path).exists():
                st.error(f"Modelo não encontrado: `{model_path}`")
                st.stop()

            with st.spinner("Lendo frames e narrando a cena..."):
                result = narrate_video(
                    video_path=video_path,
                    model_path=model_path,
                    every_n_frames=every_n,
                    max_frames=max_frames,
                    min_confidence=min_conf,
                )

            st.subheader("Narração")
            st.success(result["summary"])
            st.subheader("Detalhes por frame")
            for p in result["predictions"]:
                st.write(
                    f"**{p['timestamp_sec']:.1f}s** — {p['class']} "
                    f"({p['confidence']:.0%}): {p['caption']}"
                )
            maybe_telegram(result["summary"], video_name)
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)

else:
    st.write(
        "Aponte a webcam para a **porta**, uma pessoa **andando**, "
        "**levantando da cadeira** ou **batendo palmas**, e capture a foto."
    )
    photo = st.camera_input("Captura da webcam")

    if photo is not None and st.button(
        "Narrar captura", type="primary", use_container_width=True
    ):
        if not Path(model_path).exists():
            st.error(f"Modelo não encontrado: `{model_path}`")
            st.stop()

        file_bytes = np.asarray(bytearray(photo.read()), dtype=np.uint8)
        frame_bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        if frame_bgr is None:
            st.error("Não foi possível ler a imagem da webcam.")
            st.stop()

        with st.spinner("Classificando a cena..."):
            result = narrate_image(frame_bgr, model_path)

        st.subheader("Narração")
        st.success(result["summary"])
        st.write(
            f"**Classe:** `{result['class']}` — confiança {result['confidence']:.0%}"
        )
        probs = result.get("probabilities") or {}
        if probs:
            st.subheader("Probabilidades")
            for cls, p in sorted(probs.items(), key=lambda x: -x[1])[:5]:
                st.write(f"- {cls}: {p:.0%}")
        maybe_telegram(result["summary"], "webcam")
