# Depois do Colab — rodar no Cursor (Windows)

Você **não** abre o `.ipynb` de novo para a demo da aula.  
No Cursor você só sobe o **Streamlit** com o ONNX.

## 1) Abrir a pasta no Cursor

**File → Open Folder** →

```text
...\lia1_2026_2\Entregas - Humberto Nogueira do Carmo\Entrega 3 - Narrador de Cenas
```

Na barra lateral devem aparecer: `app/`, `models/`, `sample_data/`, `requirements.txt`.

Branch correta: `cursor/kinetics-webcam-narrador-735f` (PR #3).

## 2) Colocar o ONNX do Colab

Copie o arquivo baixado do Colab para:

```text
models\narrador_cenas.onnx
```

(substitua o antigo se já existir)

## 3) Terminal do Cursor — cole um comando por vez

Abra **Terminal → New Terminal** (PowerShell), na pasta da Entrega 3.

### Criar o ambiente

```powershell
python -m venv .venv
```

### Ativar o ambiente

```powershell
.\.venv\Scripts\Activate.ps1
```

Se aparecer erro de política de script, rode isto e ative de novo:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
.\.venv\Scripts\Activate.ps1
```

O prompt deve mostrar `(.venv)`.

### Instalar dependências

```powershell
python -m pip install -U pip
pip install -r requirements.txt
```

Se der **WinError 5** em `cv2.pyd`: feche kernels/outros Python, reinicie o Cursor, ative o `.venv` de novo e rode só o `pip install -r requirements.txt`.

## 4) Subir o Streamlit

Com `(.venv)` ativo:

```powershell
streamlit run app/streamlit_app.py
```

Abre o navegador em `http://localhost:8501`.

## 5) Demo na aula (tela compartilhada)

1. **Arquivo de vídeo** → `opening_door.mp4` (ou outro em `sample_data/`) → **Narrar cena**
2. **Webcam** → porta / andar / levantar / palmas → **Narrar captura**
3. Telegram (opcional): sidebar → **Ativar monitoramento** → token + chat id → narre de novo

## 6) Parar

No terminal: `Ctrl+C`

---

## Atalho (script)

Com a pasta da Entrega 3 aberta:

```powershell
.\scripts\setup_apresentacao.ps1
streamlit run app/streamlit_app.py
```

---

## Checklist

- [ ] Pasta Entrega 3 aberta no Cursor  
- [ ] `models\narrador_cenas.onnx` (do Colab)  
- [ ] `(.venv)` ativo  
- [ ] Streamlit em `localhost:8501`  
- [ ] Arquivo e/ou webcam narram  

A app web pública (upload / câmera IP) fica para uma fase futura.
