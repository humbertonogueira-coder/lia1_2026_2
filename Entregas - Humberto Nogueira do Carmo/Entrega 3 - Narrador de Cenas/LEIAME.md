# Entrega 3 — Narrador de Cenas (Kinetics + webcam)

Visão computacional que **lê vídeo ou webcam**, classifica ações de sala (porta, andar, levantar, palmas) e gera **narração em português**. Treino em PyTorch (CNN Residual da aula) → **ONNX** → **Streamlit** (+ Telegram).

## Pipeline

```text
Kinetics-700 subset (+ clips sentar/levantar) → frames → CNN Residual → .onnx → Streamlit (arquivo|webcam)
```

## Classes (8)

`opening_door`, `closing_door`, `walking`, `clapping`, `stretching_arm`, `pushing_cart`, `standing_up`, `sitting_down`

**Nota:** porta vem do **Kinetics-700** (não existe no Kinetics-400). Sentar/levantar = clips próprios (`scripts/prepare_custom_actions.md`).

## Apresentação (Cursor + notebook)

Siga [`ROTEIRO_APRESENTACAO.md`](ROTEIRO_APRESENTACAO.md).

## Como executar

### 1) Ambiente

```bash
cd "Entregas - Humberto Nogueira do Carmo/Entrega 3 - Narrador de Cenas"
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install ipykernel yt-dlp
```

### 2) Dados + treino + ONNX

```bash
# YouTube (pode falhar sem cookies) OU dataset demo:
python scripts/download_kinetics_subset.py
# python scripts/generate_demo_dataset.py

python scripts/build_frames_dataset.py
python scripts/train_and_export.py --epochs 12
# ou rode Narrador_de_Cenas.ipynb
```

### 3) App (arquivo ou webcam)

```bash
streamlit run app/streamlit_app.py
```

Telegram (opcional): `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID`.

## Estrutura

```text
Entrega 3 - Narrador de Cenas/
├── ROTEIRO_APRESENTACAO.md
├── Narrador_de_Cenas.ipynb
├── app/streamlit_app.py      # arquivo + webcam
├── models/narrador_cenas.onnx
├── sample_data/
└── scripts/
    ├── download_kinetics_subset.py
    ├── generate_demo_dataset.py
    ├── build_frames_dataset.py
    ├── prepare_custom_actions.md
    └── train_and_export.py
```
