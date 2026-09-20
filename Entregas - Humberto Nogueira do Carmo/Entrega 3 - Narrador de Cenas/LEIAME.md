# Entrega 3 — Narrador de Cenas

**Fluxo oficial:** Google Colab (treino + ONNX) → `Narrar.py` / Streamlit no PC (aula + Telegram AO VIVO) → app web pública (futuro).

## Pipeline

```text
Colab/GPU → CNN Residual → narrador_cenas.onnx
         ↓
PC (aula): Narrar.py + Telegram (AO VIVO)  |  Streamlit opcional
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
4. Após o `%pip`, use **Runtime → Restart session** e continue pelos imports.
5. Avisos de conflito de `protobuf` com pacotes Google do Colab podem ser ignorados se `import torch` / `import cv2` funcionarem.
6. Baixe `narrador_cenas.onnx` (a célula final chama `files.download` no Colab).

O notebook gera um dataset demo automaticamente se `data/frames` não existir. Para dados reais, prepare frames no PC e faça upload, ou use os scripts em `scripts/`.

## Fase 2 — Aula no PC (Narrar.py + Telegram AO VIVO)

Guia completo no Cursor (Windows): [`CURSOR_POS_COLAB.md`](CURSOR_POS_COLAB.md).

### Setup único

```powershell
cd "Entregas - Humberto Nogueira do Carmo\Entrega 3 - Narrador de Cenas"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# copie o ONNX do Colab para models\narrador_cenas.onnx
copy .env.example .env
# edite .env e cole TELEGRAM_BOT_TOKEN do @BotFather
```

### Na apresentação (sem digitar terminal)

1. Duplo clique em **`iniciar_narrador.bat`**
2. Cada aluno no Telegram: **`/start`** no bot → aparece o teclado **AO VIVO | PARAR**
3. Alguém toca **AO VIVO** → a webcam do PC narra e **todos os cadastrados** recebem as mensagens
4. **PARAR** encerra o vivo

### Streamlit (opcional, demo visual)

```powershell
streamlit run app/streamlit_app.py
```

Roteiro da apresentação: [`ROTEIRO_APRESENTACAO.md`](ROTEIRO_APRESENTACAO.md).

### Windows — WinError 5 (`cv2.pyd`)

Não rode o treino no Python global (`AppData\\Roaming\\Python\\...`). Use **Colab** para o ONNX. No PC use só o `.venv`. Se o pip falhar com Acesso negado em `cv2.pyd`: feche Cursor/kernels, desinstale/reinstale `opencv-python-headless` **dentro do `.venv`**.

## Fase 3 — Web pública (futuro)

Mesmo ONNX em um serviço hospedado:

- upload de vídeo
- stream de câmera IP / RTSP → frames → narração

## Estrutura

```text
Entrega 3 - Narrador de Cenas/
├── Narrar.py                 # classe + AO VIVO (webcam + Telegram)
├── iniciar_narrador.bat      # duplo clique no Windows
├── .env.example              # TELEGRAM_BOT_TOKEN=...
├── Narrador_de_Cenas.ipynb   # Colab → ONNX
├── app/streamlit_app.py      # demo visual opcional
├── app/telegram_notify.py    # cadastro + teclado AO VIVO + broadcast
├── models/narrador_cenas.onnx
├── sample_data/
└── scripts/
```
