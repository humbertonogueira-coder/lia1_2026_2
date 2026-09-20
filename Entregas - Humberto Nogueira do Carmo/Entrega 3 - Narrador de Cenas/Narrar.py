"""
Narrador de Cenas — classe + launcher (sem digitar streamlit no terminal).

Uso na aula (Windows): duplo clique em iniciar_narrador.bat
Ou: python Narrar.py
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from typing import Any, Optional

import cv2
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
APP_DIR = ROOT / "app"
sys.path.insert(0, str(APP_DIR))

load_dotenv(ROOT / ".env")

from inference import narrate_image, narrate_video  # noqa: E402
from telegram_notify import TelegramNotifier  # noqa: E402

DEFAULT_MODEL = ROOT / "models" / "narrador_cenas.onnx"


class Narrar:
    """Encapsula inferência ONNX + broadcast Telegram AO VIVO."""

    def __init__(
        self,
        model_path: Optional[str | Path] = None,
        webcam_index: Optional[int] = None,
        intervalo_s: Optional[float] = None,
        bot_token: Optional[str] = None,
    ):
        self.model_path = Path(model_path or DEFAULT_MODEL)
        self.webcam_index = int(
            webcam_index
            if webcam_index is not None
            else os.getenv("WEBCAM_INDEX", "0")
        )
        self.intervalo_s = float(
            intervalo_s
            if intervalo_s is not None
            else os.getenv("AO_VIVO_INTERVALO_S", "2")
        )
        self.telegram = TelegramNotifier(bot_token=bot_token)
        self._last_class: Optional[str] = None
        self._last_sent_at = 0.0

    def checar_modelo(self) -> None:
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Modelo ONNX não encontrado: {self.model_path}\n"
                "Copie o arquivo do Colab para models/narrador_cenas.onnx"
            )

    def narrar_frame(self, frame_bgr) -> dict[str, Any]:
        self.checar_modelo()
        return narrate_image(frame_bgr, self.model_path)

    def narrar_video(
        self,
        video_path: str | Path,
        every_n_frames: int = 15,
        max_frames: int = 30,
        min_confidence: float = 0.35,
    ) -> dict[str, Any]:
        self.checar_modelo()
        return narrate_video(
            video_path=video_path,
            model_path=self.model_path,
            every_n_frames=every_n_frames,
            max_frames=max_frames,
            min_confidence=min_confidence,
        )

    def _deve_enviar(self, classe: str, force_every_s: float = 8.0) -> bool:
        agora = time.time()
        if classe != self._last_class:
            return True
        return (agora - self._last_sent_at) >= force_every_s

    def _enviar_narracao(self, result: dict[str, Any]) -> None:
        classe = result.get("class", "?")
        conf = float(result.get("confidence") or 0.0)
        summary = result.get("summary") or result.get("caption") or ""
        texto = (
            "🔴 <b>AO VIVO</b>\n"
            f"<b>Classe:</b> <code>{classe}</code> ({conf:.0%})\n\n"
            f"{summary}"
        )
        self.telegram.broadcast(texto)
        self._last_class = classe
        self._last_sent_at = time.time()

    def capturar_frame_webcam(self):
        cap = cv2.VideoCapture(self.webcam_index)
        if not cap.isOpened():
            raise RuntimeError(
                f"Não foi possível abrir a webcam (índice {self.webcam_index})."
            )
        try:
            ok, frame = cap.read()
            if not ok or frame is None:
                raise RuntimeError("Falha ao capturar frame da webcam.")
            return frame
        finally:
            cap.release()

    def iniciar_ao_vivo(self, intervalo_s: Optional[float] = None) -> None:
        """Captura webcam em loop enquanto Telegram estiver em AO VIVO."""
        self.checar_modelo()
        intervalo = float(intervalo_s if intervalo_s is not None else self.intervalo_s)
        print(f"[AO VIVO] Webcam {self.webcam_index} | intervalo {intervalo}s")
        print("[AO VIVO] Ctrl+C para sair.")

        while self.telegram.live_requested:
            # Processa teclado PARAR / novos /start sem bloquear demais
            self.telegram.poll_updates(timeout=1)
            if not self.telegram.live_requested:
                break
            try:
                frame = self.capturar_frame_webcam()
                result = self.narrar_frame(frame)
                if self._deve_enviar(result["class"]):
                    print(
                        f"  → {result['class']} ({result['confidence']:.0%}): "
                        f"{result.get('summary', '')}"
                    )
                    if self.telegram.configured:
                        self._enviar_narracao(result)
            except Exception as exc:  # noqa: BLE001
                print(f"[AO VIVO] aviso: {exc}")
            # Espera intervalo, mas continua escutando o bot
            fim = time.time() + intervalo
            while time.time() < fim and self.telegram.live_requested:
                restante = max(0.2, min(1.0, fim - time.time()))
                self.telegram.poll_updates(timeout=restante)

        print("[AO VIVO] pausado.")

    def rodar(self) -> None:
        """Loop principal: escuta Telegram e liga AO VIVO sob demanda."""
        print("=" * 50)
        print("  Narrador de Cenas")
        print("=" * 50)
        try:
            self.checar_modelo()
            print(f"Modelo: {self.model_path}")
        except FileNotFoundError as exc:
            print(exc)
            print("Coloque o ONNX e rode de novo.")
            return

        if not self.telegram.configured:
            print(
                "\nAVISO: TELEGRAM_BOT_TOKEN vazio no .env\n"
                "Copie .env.example → .env e cole o token do @BotFather.\n"
                "Sem token, o bot não inicia (modo local só com webcam de teste)."
            )
            print("\nTeste local: narrando 1 frame da webcam…")
            try:
                frame = self.capturar_frame_webcam()
                result = self.narrar_frame(frame)
                print(result.get("summary") or result)
            except Exception as exc:  # noqa: BLE001
                print(f"Falha no teste local: {exc}")
            return

        print("Telegram OK. Peça aos alunos: /start no bot.")
        print("Teclado: AO VIVO | PARAR")
        print("Aguardando… (Ctrl+C encerra)\n")

        try:
            while True:
                live = self.telegram.poll_updates(timeout=25)
                if live:
                    self.iniciar_ao_vivo()
        except KeyboardInterrupt:
            print("\nEncerrado.")


def main() -> None:
    Narrar().rodar()


if __name__ == "__main__":
    main()
