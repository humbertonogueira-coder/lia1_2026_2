# Entrega 3 — Narrador de Cenas

**Fluxo oficial:** Google Colab (treino + ONNX) → Streamlit no PC (aula + Telegram) → app web pública (futuro).

## Pipeline

```text
Colab/GPU → CNN Residual → narrador_cenas.onnx
         ↓
PC (aula): Streamlit (arquivo | webcam) + Telegram
         ↓
Futuro: web pública (upload / câmera IP)
```

## Classes (8)

`opening_door`, `closing_door`, `walking`, `clapping`, `stretching_arm`, `pushing_cart`, `standing_up`, `sitting_down`

- Porta: **Kinetics-700** (`opening door` / `closing door` não existem no Kinetics-400).
- Sentar/levantar: clips próprios (`scripts/prepare_custom_actions.md`) ou dataset demo no Colab.

## Fase 1 — Colab (até o ONNX)

1. Abra [`Narrador_de_Cenas.ipynb`](Narrador_de_Cenas.ipynb) no Google Colab (upload ou Drive).
2. **Runtime → Change runtime type → GPU** (opcional).
3. Execute as células até a exportação ONNX.
4. Baixe `narrador_cenas.onnx` (a célula final chama `files.download` no Colab).

O notebook gera um dataset demo automaticamente se `data/frames` não existir. Para dados reais, prepare frames no PC e faça upload, ou use os scripts em `scripts/`.

## Fase 2 — Aula no PC (Streamlit + Telegram)

```bash
cd "Entregas - Humberto Nogueira do Carmo/Entrega 3 - Narrador de Cenas"
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt

# copie o ONNX baixado do Colab para models/narrador_cenas.onnx
streamlit run app/streamlit_app.py
```

- Compartilhe a tela do navegador (`localhost:8501`).
- Modo **Webcam** para porta / andar / levantar / palmas.
- Telegram: toggle **Ativar monitoramento** + `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID`.

Roteiro detalhado: [`ROTEIRO_APRESENTACAO.md`](ROTEIRO_APRESENTACAO.md).

### Windows — WinError 5 (`cv2.pyd`)

Não rode o treino no Python global (`AppData\\Roaming\\Python\\...`). Use **Colab** para o ONNX. No PC use só o `.venv` do Streamlit. Se o pip falhar com Acesso negado em `cv2.pyd`: feche Cursor/kernels, desinstale/reinstale `opencv-python-headless` **dentro do `.venv`**.

## Fase 3 — Web pública (futuro)

Mesmo ONNX em um serviço hospedado:

- upload de vídeo
- stream de câmera IP / RTSP → frames → narração

## Estrutura

```text
Entrega 3 - Narrador de Cenas/
├── Narrador_de_Cenas.ipynb   # Colab → ONNX
├── ROTEIRO_APRESENTACAO.md
├── app/streamlit_app.py      # arquivo + webcam + Telegram
├── models/narrador_cenas.onnx
├── sample_data/
└── scripts/
```
