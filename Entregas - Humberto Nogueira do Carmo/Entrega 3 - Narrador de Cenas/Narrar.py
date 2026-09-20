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

    def _abrir_webcam(self):
        """Abre a webcam e descarta alguns frames iniciais (foco/exposição)."""
        # CAP_DSHOW evita travar em muitos notebooks Windows
        cap = cv2.VideoCapture(self.webcam_index, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(self.webcam_index)
        if not cap.isOpened():
            raise RuntimeError(
                f"Não foi possível abrir a webcam (índice {self.webcam_index}).\n"
                "Feche Zoom/Teams/Camera app, permita acesso à câmera no Windows "
                "e confira WEBCAM_INDEX no .env (tente 0 ou 1)."
            )
        for _ in range(5):
            cap.read()
        return cap

    def capturar_frame_webcam(self):
        cap = self._abrir_webcam()
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
        print(f"[AO VIVO] Abrindo webcam {self.webcam_index}…")
        print("[AO VIVO] PARAR no Telegram, tecla Q (se houver janela) ou Ctrl+C.")

        cap = None
        preview = None
        mostrar_janela = True
        janela = "Narrador AO VIVO"
        try:
            cap = self._abrir_webcam()
            print("[AO VIVO] Webcam ligada. Narrando…")
        except Exception as exc:  # noqa: BLE001
            print(f"[AO VIVO] ERRO ao abrir câmera: {exc}")
            self.telegram.live_requested = False
            if self.telegram.configured:
                self.telegram.broadcast(
                    f"⚠️ Não foi possível abrir a webcam do PC.\n<code>{exc}</code>"
                )
            return

        try:
            while self.telegram.live_requested:
                self.telegram.poll_updates(timeout=0)
                if not self.telegram.live_requested:
                    break
                try:
                    ok, frame = cap.read()
                    if not ok or frame is None:
                        raise RuntimeError("Falha ao ler frame da webcam.")

                    preview = frame.copy()
                    cv2.putText(
                        preview,
                        "AO VIVO - Q para fechar",
                        (12, 28),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 200, 0),
                        2,
                        cv2.LINE_AA,
                    )
                    if mostrar_janela:
                        try:
                            cv2.imshow(janela, preview)
                            tecla = cv2.waitKey(1) & 0xFF
                            if tecla in (ord("q"), ord("Q"), 27):
                                self.telegram.live_requested = False
                                break
                        except Exception:  # noqa: BLE001
                            # opencv-python-headless não tem GUI — segue sem janela
                            mostrar_janela = False
                            print(
                                "[AO VIVO] Sem janela de preview "
                                "(instale opencv-python se quiser ver a câmera)."
                            )

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

                fim = time.time() + intervalo
                while time.time() < fim and self.telegram.live_requested:
                    if mostrar_janela and preview is not None:
                        try:
                            cv2.imshow(janela, preview)
                            tecla = cv2.waitKey(1) & 0xFF
                            if tecla in (ord("q"), ord("Q"), 27):
                                self.telegram.live_requested = False
                                break
                        except Exception:  # noqa: BLE001
                            mostrar_janela = False
                    restante = max(0.05, min(0.4, fim - time.time()))
                    self.telegram.poll_updates(timeout=restante)
        finally:
            if cap is not None:
                cap.release()
            try:
                cv2.destroyAllWindows()
            except Exception:  # noqa: BLE001
                pass
            print("[AO VIVO] Webcam desligada / pausado.")

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
        print("A webcam SÓ liga depois que alguém tocar em AO VIVO no Telegram.")
        print("Aguardando… (Ctrl+C encerra)\n")

        try:
            while True:
                live = self.telegram.poll_updates(timeout=25)
                if live:
                    print("\n>>> AO VIVO recebido no Telegram — ligando webcam…\n")
                    self.iniciar_ao_vivo()
                    print("\nAguardando novo AO VIVO… (Ctrl+C encerra)\n")
        except KeyboardInterrupt:
            print("\nEncerrado.")
            cv2.destroyAllWindows()


def main() -> None:
    Narrar().rodar()


if __name__ == "__main__":
    main()
