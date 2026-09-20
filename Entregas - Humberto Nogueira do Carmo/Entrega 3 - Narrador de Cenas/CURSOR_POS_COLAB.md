# Depois do Colab — rodar no Cursor (Windows)

Você **não** abre o `.ipynb` de novo para a demo da aula.  
No Cursor você sobe o **Narrador** com o ONNX (preferência: `Narrar.py` / `.bat`).

## 1) Abrir a pasta no Cursor

**File → Open Folder** →

```text
...\lia1_2026_2\Entregas - Humberto Nogueira do Carmo\Entrega 3 - Narrador de Cenas
```

Na barra lateral devem aparecer: `app/`, `models/`, `sample_data/`, `Narrar.py`, `iniciar_narrador.bat`, `requirements.txt`.

## 2) Colocar o ONNX do Colab

Copie o arquivo baixado do Colab para:

```text
models\narrador_cenas.onnx
```

(substitua o antigo se já existir)

## 3) Ambiente (só na primeira vez)

Abra **Terminal → New Terminal** (PowerShell), na pasta da Entrega 3.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -r requirements.txt
copy .env.example .env
```

Se aparecer erro de política de script:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
.\.venv\Scripts\Activate.ps1
```

Se der **WinError 5** em `cv2.pyd`: feche kernels/outros Python, reinicie o Cursor, ative o `.venv` de novo e rode só o `pip install -r requirements.txt`.

## 4) Token do Telegram (`.env`)

1. No Telegram, abra **@BotFather** → `/newbot` (ou use um bot já criado).
2. Copie o token.
3. Abra o arquivo `.env` na pasta da Entrega 3 e preencha:

```text
TELEGRAM_BOT_TOKEN=123456:ABC-seu-token-aqui
```

`TELEGRAM_ADMIN_CHAT_ID` é opcional.

## 5) Demo na aula — sem terminal

**Duplo clique** em:

```text
iniciar_narrador.bat
```

(isso ativa o `.venv` e roda `python Narrar.py`)

No Telegram:

1. Cada aluno manda **`/start`** no bot → recebe o teclado **AO VIVO | PARAR** e fica cadastrado.
2. Alguém toca **AO VIVO** → a webcam do PC classifica a cena e **todos os cadastrados** recebem a narração.
3. **PARAR** encerra o vivo.
4. Na janela do `.bat`, `Ctrl+C` (ou feche) encerra o programa.

## 6) Streamlit (opcional)

Com `(.venv)` ativo:

```powershell
streamlit run app/streamlit_app.py
```

Abre `http://localhost:8501` (arquivo / webcam na tela). O monitoramento Telegram envia broadcast aos cadastrados (`/start`).

---

## Atalho de setup

```powershell
.\scripts\setup_apresentacao.ps1
```

Depois: duplo clique em `iniciar_narrador.bat` **ou** `streamlit run app/streamlit_app.py`.

---

## Checklist

- [ ] Pasta Entrega 3 aberta no Cursor  
- [ ] `models\narrador_cenas.onnx` (do Colab)  
- [ ] `.venv` criado + `pip install -r requirements.txt`  
- [ ] `.env` com `TELEGRAM_BOT_TOKEN`  
- [ ] `iniciar_narrador.bat` abre sem erro  
- [ ] Alunos: `/start` → teclado AO VIVO  
- [ ] AO VIVO narra e chega no Telegram  

A app web pública (upload / câmera IP) fica para uma fase futura.
