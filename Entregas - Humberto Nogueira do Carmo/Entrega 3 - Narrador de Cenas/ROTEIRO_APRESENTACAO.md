# Roteiro de apresentação — Colab → Streamlit → Telegram

## Visão geral

| Fase | Onde | O que fazer |
|------|------|-------------|
| 1 | **Google Colab** | Treinar CNN, gerar e baixar `narrador_cenas.onnx` |
| 2 | **PC na sala** | Streamlit + webcam + Telegram (tela compartilhada) |
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
# copie o ONNX do Colab para models\narrador_cenas.onnx
streamlit run app/streamlit_app.py
```

Teste em casa: arquivo `opening_door.mp4` + uma captura de webcam.

### C) Telegram (opcional)

1. `@BotFather` → token  
2. Chat id  
3. Anote para colar na sidebar do Streamlit  

---

## No dia (~10–15 min)

### 1) Contexto (1 min)
- Colab gerou o ONNX; agora a app consome o modelo.
- Ações: porta, andar, levantar, palmas.

### 2) (Opcional) Mostrar 30s do Colab
- Abrir o notebook já executado / curvas / arquivo ONNX baixado.

### 3) Streamlit na tela compartilhada (5–7 min)
```bash
streamlit run app/streamlit_app.py
```
Ordem:
1. **Arquivo** → `opening_door.mp4`
2. **Webcam** → porta / andar / levantar / palmas → **Narrar captura**
3. Telegram com monitoramento ligado

### 4) Fechamento
```text
Colab → ONNX → Streamlit (webcam) → Telegram
```
Próximo passo do projeto: web pública com upload e câmera IP.

---

## Plano B

| Problema | Ação |
|----------|------|
| Colab sem GPU / sem tempo | Use `models/narrador_cenas.onnx` já no repositório |
| WinError 5 no Windows | Não treine no PC; só Streamlit no `.venv` |
| Webcam sem permissão | Use só `sample_data/` |
| Telegram falha | Mostre a narração na tela |

## O que NÃO fazer no Colab na apresentação
- Streamlit ao vivo
- Webcam da sala
- Bot Telegram estável  

Isso fica no **seu computador**.
