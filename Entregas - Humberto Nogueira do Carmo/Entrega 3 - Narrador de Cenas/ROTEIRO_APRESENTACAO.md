# Roteiro de apresentação — Colab → Narrar.py / Telegram AO VIVO

## Visão geral

| Fase | Onde | O que fazer |
|------|------|-------------|
| 1 | **Google Colab** | Treinar CNN, gerar e baixar `narrador_cenas.onnx` |
| 2 | **PC na sala** | `iniciar_narrador.bat` + Telegram AO VIVO (Streamlit opcional) |
| 3 | Futuro | App web pública (upload / câmera IP) |

## Classes da demo (8)

| Classe | Narração |
|--------|----------|
| `opening_door` | abrindo a porta |
| `closing_door` | fechando a porta |
| `walking` | pessoa andando |
| `clapping` | batendo palmas |
| `stretching_arm` | alongando o braço |
| `pushing_cart` | empurrando carrinho |
| `standing_up` | levantando da cadeira |
| `sitting_down` | sentando |

---

## Antes do dia

### A) Colab (obrigatório se for gerar ONNX novo)

1. Faça upload de `Narrador_de_Cenas.ipynb` no Colab (ou abra pelo Drive).
2. Runtime → GPU.
3. Execute todas as células até o download do `.onnx`.
4. Guarde `narrador_cenas.onnx` (já existe um no repo em `models/` se quiser pular o treino).

### B) PC da aula (Cursor)

Guia detalhado: [`CURSOR_POS_COLAB.md`](CURSOR_POS_COLAB.md).

```powershell
cd "Entregas - Humberto Nogueira do Carmo\Entrega 3 - Narrador de Cenas"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# edite .env → TELEGRAM_BOT_TOKEN do @BotFather
# copie o ONNX do Colab para models\narrador_cenas.onnx
```

Teste em casa: duplo clique em `iniciar_narrador.bat` + `/start` no bot.

### C) Telegram

1. `@BotFather` → token no `.env` (`TELEGRAM_BOT_TOKEN=...`)
2. No dia: alunos mandam `/start` → teclado **AO VIVO | PARAR**

---

## No dia (~10–15 min)

### 1) Contexto (1 min)
- Colab gerou o ONNX; agora o PC narra ao vivo.
- Ações: porta, andar, levantar, palmas.

### 2) (Opcional) Mostrar 30s do Colab
- Abrir o notebook já executado / curvas / arquivo ONNX baixado.

### 3) AO VIVO na sala (5–7 min)
1. Duplo clique em **`iniciar_narrador.bat`**
2. Alunos: **`/start`** no bot
3. Alguém toca **AO VIVO** → webcam do PC → narração no Telegram de todos
4. Demonstrar porta / andar / levantar / palmas
5. **PARAR**

### 4) (Opcional) Streamlit na tela
```bash
streamlit run app/streamlit_app.py
```
Arquivo `opening_door.mp4` + captura webcam.

### 5) Fechamento
```text
Colab → ONNX → Narrar.py (webcam) → Telegram AO VIVO
```
Próximo passo do projeto: web pública com upload e câmera IP.

---

## Plano B

| Problema | Ação |
|----------|------|
| Colab sem GPU / sem tempo | Use `models/narrador_cenas.onnx` já no repositório |
| WinError 5 no Windows | Não treine no PC; só `.venv` + `iniciar_narrador.bat` |
| Webcam sem permissão | Use Streamlit + `sample_data/` |
| Telegram falha / token vazio | Mostre a narração no console do `.bat` ou no Streamlit |

## O que NÃO fazer no Colab na apresentação
- Streamlit ao vivo
- Webcam da sala
- Bot Telegram estável  

Isso fica no **seu computador**.
