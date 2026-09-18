# Roteiro de apresentação — Cursor + notebook + webcam

Objetivo: **vídeo/webcam → ação → texto em português → ONNX → Streamlit → Telegram**.

## Classes da demo (8)

| Classe | Narração | Origem dos dados |
|--------|----------|------------------|
| `opening_door` | abrindo a porta | Kinetics-700 |
| `closing_door` | fechando a porta | Kinetics-700 |
| `walking` | pessoa andando | Kinetics (`walking the dog`) |
| `clapping` | batendo palmas | Kinetics |
| `stretching_arm` | alongando o braço | Kinetics |
| `pushing_cart` | empurrando carrinho | Kinetics |
| `standing_up` | levantando da cadeira | clips próprios |
| `sitting_down` | sentando | clips próprios |

> `opening door` / `closing door` **não existem no Kinetics-400** — usamos anotações do Kinetics-700-2020.

---

## Antes do dia

1. Abrir a pasta da Entrega 3 no Cursor.
2. Setup:
   ```bash
   bash scripts/setup_apresentacao.sh   # ou .ps1 no Windows
   ```
3. Dados (escolha uma):
   - **Real (aula):** `python scripts/download_kinetics_subset.py` + clips em `data/custom_actions/` ([`prepare_custom_actions.md`](scripts/prepare_custom_actions.md))
   - **Pipeline rápido:** `python scripts/generate_demo_dataset.py` (sintético; só para testar o fluxo)
4. `python scripts/build_frames_dataset.py`
5. Treinar / exportar: rode `Narrador_de_Cenas.ipynb` **ou** `python scripts/train_and_export.py`
6. Confirme `models/narrador_cenas.onnx` e `sample_data/*.mp4`

---

## No dia (~10–15 min)

### 1) Contexto (1 min)
- Problema: narrar o que acontece (porta, andar, levantar).
- Mesma CNN Residual da aula → ONNX.

### 2) Notebook (5 min)
- Abra `Narrador_de_Cenas.ipynb`, kernel `.venv` / Python (Narrador).
- Mostre dados → CNN → métricas → export ONNX.
- Atalho: se treino demorar, use o `.onnx` já gerado.

### 3) Streamlit + webcam (5 min)
```bash
streamlit run app/streamlit_app.py
```
Ordem da demo:
1. **Arquivo** → `opening_door.mp4` (ou real)
2. **Webcam** → apontar para porta / pessoa andando / levantar / palmas → **Narrar captura**
3. (Opcional) Telegram com monitoramento ligado

### 4) Fechamento
```text
Kinetics/custom → frames → CNN → .onnx → Streamlit (arquivo|webcam) → Telegram
```

## Plano B
| Problema | Ação |
|----------|------|
| YouTube bloqueia Kinetics | `generate_demo_dataset.py` + explique que na máquina local usa download + cookies |
| Webcam sem permissão | Use só `sample_data/` |
| Sentar/levantar fraco | Grave clips reais (`prepare_custom_actions.md`) e retreine |
