# Entrega 3 — Narrador de Cenas

Aplicação de visão computacional que **lê um vídeo**, classifica ações quadro a quadro (subset do **UCF-101**) e gera uma **narração em português**. O modelo é treinado em PyTorch (CNN Residual da aula), exportado para **ONNX** e consumido por um app **Streamlit**, com opção de **monitoramento via Telegram**.

## Pipeline

```text
UCF-101 subset → frames → CNN Residual → .onnx → Streamlit (+ Telegram)
```

## Classes (10 ações)

ApplyEyeMakeup, ApplyLipstick, Archery, BabyCrawling, BalanceBeam, BandMarching, BaseballPitch, Basketball, BasketballDunk, BenchPress

## Apresentação (Cursor + notebook)

Siga o roteiro em [`ROTEIRO_APRESENTACAO.md`](ROTEIRO_APRESENTACAO.md).  
Setup rápido: `scripts/setup_apresentacao.sh` (Linux/macOS) ou `scripts/setup_apresentacao.ps1` (Windows).

## Como executar

### 1) Ambiente

```bash
cd "Entregas - Humberto Nogueira do Carmo/Entrega 3 - Narrador de Cenas"
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install ipykernel
python -m ipykernel install --user --name narrador-cenas --display-name "Python (Narrador)"
```

No Cursor, abra `Narrador_de_Cenas.ipynb` e selecione o kernel **Python (Narrador)**.

### 2) Treinar e exportar ONNX

No Colab/local, rode o notebook `Narrador_de_Cenas.ipynb` **ou**:

```bash
# baixa o subset (se ainda não existir) e treina
python scripts/download_ucf_subset.py
python scripts/train_and_export.py --epochs 12
```

O artefato sai em `models/narrador_cenas.onnx`.

### 3) App web (Streamlit)

```bash
streamlit run app/streamlit_app.py
```

- Faça upload de um vídeo **ou** use um exemplo em `sample_data/`
- Ative **Monitoramento** e informe `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` para receber a narração no Telegram

Variáveis de ambiente (opcional):

```bash
export TELEGRAM_BOT_TOKEN="123:ABC..."
export TELEGRAM_CHAT_ID="999999999"
```

## Telegram — monitoramento

1. Crie um bot com [@BotFather](https://t.me/BotFather) e copie o token  
2. Envie `/start` ao bot e descubra o chat id (ex.: via `@userinfobot`)  
3. No Streamlit, ligue **Ativar monitoramento** e narre um vídeo — a cena lida é enviada como mensagem

## Estrutura

```text
Entrega 3 - Narrador de Cenas/
├── ROTEIRO_APRESENTACAO.md   # passos para apresentar no Cursor
├── Narrador_de_Cenas.ipynb   # aula: treino + métricas + ONNX
├── app/
│   ├── streamlit_app.py
│   ├── inference.py
│   ├── narration.py
│   ├── telegram_notify.py
│   └── model_arch.py
├── scripts/
│   ├── setup_apresentacao.sh / .ps1
│   ├── download_ucf_subset.py
│   └── train_and_export.py
├── models/narrador_cenas.onnx
├── sample_data/              # vídeos de exemplo
└── requirements.txt
```

## Observação pedagógica

Narração completa livre (captioning open-ended) exigiria modelos de linguagem multimodal pesados. Nesta entrega, a estratégia alinhada à aula é: **classificação de ação por frame → templates de narração → ONNX deployável**, cobrindo o ciclo completo até a aplicação web e o alerta no Telegram.
