"""
Narrador de Cenas — Streamlit
Upload de vídeo → inferência ONNX → narração + alerta Telegram (monitoramento)
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import streamlit as st

APP_DIR = Path(__file__).resolve().parent
ROOT = APP_DIR.parent
sys.path.insert(0, str(APP_DIR))

from inference import narrate_video  # noqa: E402
from telegram_notify import TelegramNotifier  # noqa: E402

DEFAULT_MODEL = ROOT / "models" / "narrador_cenas.onnx"

st.set_page_config(
    page_title="Narrador de Cenas",
    page_icon="🎬",
    layout="centered",
)

st.title("Narrador de Cenas")
st.caption(
    "Classifica ações em frames de vídeo (UCF-101 / ONNX) e gera uma narração em português."
)

with st.sidebar:
    st.header("Configuração")
    model_path = st.text_input("Caminho do modelo ONNX", value=str(DEFAULT_MODEL))
    every_n = st.slider("Amostrar 1 frame a cada N", min_value=5, max_value=60, value=15)
    max_frames = st.slider("Máximo de frames", min_value=5, max_value=80, value=30)
    min_conf = st.slider("Confiança mínima", 0.1, 0.9, 0.35, 0.05)

    st.divider()
    st.subheader("Monitoramento Telegram")
    monitoring = st.toggle(
        "Ativar monitoramento",
        value=False,
        help="Quando ativo, a narração da cena é enviada ao Telegram.",
    )
    bot_token = st.text_input(
        "Bot token",
        value=os.getenv("TELEGRAM_BOT_TOKEN", ""),
        type="password",
    )
    chat_id = st.text_input("Chat ID", value=os.getenv("TELEGRAM_CHAT_ID", ""))

uploaded = st.file_uploader(
    "Envie um vídeo (.avi, .mp4, .mov, .mkv)",
    type=["avi", "mp4", "mov", "mkv"],
)

sample_dir = ROOT / "sample_data"
sample_videos = sorted(sample_dir.glob("*.avi")) if sample_dir.exists() else []
sample_choice = None
if sample_videos:
    sample_choice = st.selectbox(
        "Ou use um vídeo de exemplo",
        options=["(nenhum)"] + [p.name for p in sample_videos],
    )

run = st.button("Narrar cena", type="primary", use_container_width=True)

if run:
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
            st.error(
                f"Modelo não encontrado em `{model_path}`. "
                "Execute o notebook de treinamento primeiro."
            )
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

        if monitoring:
            notifier = TelegramNotifier(bot_token=bot_token, chat_id=chat_id)
            if not notifier.configured:
                st.warning(
                    "Monitoramento ligado, mas token/chat_id estão vazios. "
                    "Preencha na barra lateral ou exporte as variáveis de ambiente."
                )
            else:
                try:
                    notifier.send_scene_alert(result["summary"], video_name=video_name)
                    st.info("Aviso enviado ao Telegram.")
                except Exception as exc:  # noqa: BLE001
                    st.error(f"Falha ao enviar ao Telegram: {exc}")

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
