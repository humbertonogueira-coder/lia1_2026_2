# Roteiro de apresentação — Cursor + notebook

Objetivo na fala: **vídeo → classificação de ação → texto em português → ONNX → app web → alerta Telegram**.

Ambiente: **Cursor** (abrir o notebook `.ipynb` direto no editor).

---

## Antes do dia (preparar em casa)

### 1) Abrir o projeto no Cursor
- Repo: `lia1_2026_2`
- Pasta da entrega: `Entregas - Humberto Nogueira do Carmo/Entrega 3 - Narrador de Cenas/`

### 2) Criar o ambiente Python (terminal do Cursor)

**Windows:**
```powershell
cd "Entregas - Humberto Nogueira do Carmo/Entrega 3 - Narrador de Cenas"
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
pip install ipykernel
python -m ipykernel install --user --name narrador-cenas --display-name "Python (Narrador)"
```

**Linux / macOS:**
```bash
cd "Entregas - Humberto Nogueira do Carmo/Entrega 3 - Narrador de Cenas"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install ipykernel
python -m ipykernel install --user --name narrador-cenas --display-name "Python (Narrador)"
```

Ou use o script: `scripts/setup_apresentacao.sh` (Linux/macOS) / `scripts/setup_apresentacao.ps1` (Windows).

### 3) Conferir artefatos
- `models/narrador_cenas.onnx` (já no repositório)
- `sample_data/Basketball.avi` (e outros exemplos)
- `Narrador_de_Cenas.ipynb`

### 4) Kernel no Cursor
1. Abra `Narrador_de_Cenas.ipynb` no Cursor.
2. Clique no seletor de kernel (canto superior direito do notebook).
3. Escolha **Python (Narrador)** ou o interpretador `.venv` da pasta da entrega.
4. Rode **uma célula** de teste (`print("ok")` ou a de imports) para validar.

### 5) Telegram (opcional)
1. `@BotFather` → criar bot → copiar token.
2. Descubra o chat id (ex.: `@userinfobot`).
3. Anote `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID`.

### 6) Ensaio rápido
- Notebook: rode pelo menos imports + seção de narração/ONNX (ou use o modelo pronto se o treino demorar).
- Streamlit: `streamlit run app/streamlit_app.py` → narrar `Basketball.avi`.

---

## No dia — sequência (~10–15 min)

### 1) Contexto (1 min)
- Problema: narrar o que acontece em um vídeo.
- Dataset: **UCF-101 subset** (10 ações).
- Estratégia da aula: CNN Residual → **ONNX** → aplicação.

### 2) Notebook no Cursor (5–7 min)
1. Abra `Narrador_de_Cenas.ipynb`.
2. Confirme o kernel **Python (Narrador)** / `.venv`.
3. Mostre célula a célula:
   - download/extração do subset
   - frames → `ImageFolder`
   - arquitetura CNN Residual
   - treino + matriz de confusão
   - narração de um vídeo
   - exportação do `.onnx`
4. **Atalho se rede/treino falhar:** diga que o modelo já está em `models/narrador_cenas.onnx` e vá para o Streamlit.

### 3) Demo Streamlit (3–5 min)
No terminal do Cursor (`.venv` ativo):

```bash
streamlit run app/streamlit_app.py
```

1. Escolha `Basketball.avi` em `sample_data/`.
2. Clique **Narrar cena**.
3. Mostre o resumo em português + detalhes por frame.
4. Se tiver Telegram: ligue **Ativar monitoramento**, cole token/chat id, narre de novo e mostre no celular.

### 4) Fechamento (1 min)

```text
UCF-101 → frames → CNN → .onnx → Streamlit → Telegram
```

Arquivos-chave: `Narrador_de_Cenas.ipynb`, `models/narrador_cenas.onnx`, `app/streamlit_app.py`.

---

## Plano B

| Problema | O que fazer |
|----------|-------------|
| Kernel errado no Cursor | Seletor do notebook → `.venv` / Python (Narrador) |
| Sem internet | Não baixar dataset; use ONNX pronto + Streamlit |
| Streamlit não abre | `pip install -r requirements.txt`; porta `8501` |
| Telegram falha | Mostre só a narração na tela; explique o fluxo |

## Telegram — o que falar
- Não é obrigatório para a demo funcionar.
- Fluxo: usuário ativa monitoramento → app envia o **texto da cena** lido do vídeo via Bot API.
