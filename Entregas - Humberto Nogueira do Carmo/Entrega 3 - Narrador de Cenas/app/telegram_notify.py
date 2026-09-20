"""Cliente Telegram: cadastro, teclado AO VIVO e broadcast de narrações."""

from __future__ import annotations

import json
import os
import threading
from pathlib import Path
from typing import Any, Optional

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

DEFAULT_SUBSCRIBERS_PATH = ROOT / "data" / "telegram_subscribers.json"

BTN_AO_VIVO = "AO VIVO"
BTN_PARAR = "PARAR"


class TelegramNotifier:
    def __init__(
        self,
        bot_token: Optional[str] = None,
        subscribers_path: Optional[str | Path] = None,
    ):
        self.bot_token = (bot_token or os.getenv("TELEGRAM_BOT_TOKEN", "")).strip()
        self.admin_chat_id = os.getenv("TELEGRAM_ADMIN_CHAT_ID", "").strip()
        self.subscribers_path = Path(
            subscribers_path or DEFAULT_SUBSCRIBERS_PATH
        )
        self._lock = threading.Lock()
        self._offset = 0
        self.live_requested = False
        self._ensure_store()

    @property
    def configured(self) -> bool:
        return bool(self.bot_token)

    def _api(self, method: str, **kwargs: Any) -> dict[str, Any]:
        if not self.configured:
            raise RuntimeError(
                "Telegram não configurado. Defina TELEGRAM_BOT_TOKEN no .env."
            )
        url = f"https://api.telegram.org/bot{self.bot_token}/{method}"
        resp = requests.post(url, json=kwargs, timeout=35)
        resp.raise_for_status()
        data = resp.json()
        if not data.get("ok", False):
            raise RuntimeError(f"Telegram API erro: {data}")
        return data

    def _ensure_store(self) -> None:
        self.subscribers_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.subscribers_path.exists():
            self._save_ids([])

    def _load_ids(self) -> list[str]:
        try:
            raw = json.loads(self.subscribers_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        if isinstance(raw, dict):
            ids = raw.get("chat_ids", [])
        elif isinstance(raw, list):
            ids = raw
        else:
            ids = []
        return [str(x) for x in ids if str(x).strip()]

    def _save_ids(self, ids: list[str]) -> None:
        unique = sorted(set(str(i) for i in ids if str(i).strip()))
        payload = {"chat_ids": unique}
        self.subscribers_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    def list_subscribers(self) -> list[str]:
        with self._lock:
            return self._load_ids()

    def register(self, chat_id: str | int) -> bool:
        cid = str(chat_id).strip()
        if not cid:
            return False
        with self._lock:
            ids = self._load_ids()
            if cid in ids:
                return False
            ids.append(cid)
            self._save_ids(ids)
            return True

    def unregister(self, chat_id: str | int) -> bool:
        cid = str(chat_id).strip()
        with self._lock:
            ids = self._load_ids()
            if cid not in ids:
                return False
            ids = [i for i in ids if i != cid]
            self._save_ids(ids)
            return True

    def keyboard_markup(self) -> dict[str, Any]:
        return {
            "keyboard": [[{"text": BTN_AO_VIVO}, {"text": BTN_PARAR}]],
            "resize_keyboard": True,
            "one_time_keyboard": False,
        }

    def send_message(
        self,
        text: str,
        chat_id: Optional[str | int] = None,
        parse_mode: str = "HTML",
        reply_markup: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        target = str(chat_id or self.admin_chat_id or "").strip()
        if not target:
            raise RuntimeError("chat_id ausente para send_message.")
        payload: dict[str, Any] = {
            "chat_id": target,
            "text": text[:4000],
            "parse_mode": parse_mode,
            "disable_web_page_preview": True,
        }
        if reply_markup is not None:
            payload["reply_markup"] = reply_markup
        return self._api("sendMessage", **payload)

    def send_keyboard(self, chat_id: str | int, text: str | None = None) -> dict[str, Any]:
        msg = text or (
            "Bem-vindo ao <b>Narrador de Cenas</b>.\n"
            f"Use o teclado: <b>{BTN_AO_VIVO}</b> para receber narrações da webcam "
            f"ou <b>{BTN_PARAR}</b> para pausar."
        )
        return self.send_message(
            msg,
            chat_id=chat_id,
            reply_markup=self.keyboard_markup(),
        )

    def broadcast(self, text: str, parse_mode: str = "HTML") -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for cid in self.list_subscribers():
            try:
                results.append(self.send_message(text, chat_id=cid, parse_mode=parse_mode))
            except Exception as exc:  # noqa: BLE001
                results.append({"ok": False, "chat_id": cid, "error": str(exc)})
        return results

    def send_scene_alert(self, summary: str, video_name: str = "") -> list[dict[str, Any]]:
        header = "🎬 <b>Monitoramento de cena</b>"
        if video_name:
            header += f"\n📁 <code>{video_name}</code>"
        body = f"{header}\n\n{summary}"
        return self.broadcast(body)

    def _handle_update(self, update: dict[str, Any]) -> None:
        message = update.get("message") or update.get("edited_message") or {}
        chat = message.get("chat") or {}
        chat_id = chat.get("id")
        if chat_id is None:
            return
        text = (message.get("text") or "").strip()
        if not text:
            return

        lower = text.lower()
        if lower.startswith("/start"):
            self.register(chat_id)
            self.send_keyboard(chat_id)
            return

        if lower.startswith("/stop") or text == BTN_PARAR:
            was_live = self.live_requested
            self.live_requested = False
            self.send_message(
                "⏹️ AO VIVO pausado. Toque em <b>AO VIVO</b> para retomar.",
                chat_id=chat_id,
                reply_markup=self.keyboard_markup(),
            )
            if was_live:
                self.broadcast(
                    "⏹️ <b>AO VIVO</b> encerrado pelo usuário.",
                )
            return

        if text == BTN_AO_VIVO or lower in {"ao vivo", "/ao_vivo", "/aovivo"}:
            self.register(chat_id)
            self.live_requested = True
            n = len(self.list_subscribers())
            self.broadcast(
                "🔴 <b>AO VIVO</b> iniciado.\n"
                f"Cadastrados: {n}. Aguardando narrações da webcam…"
            )
            return

        self.register(chat_id)
        self.send_keyboard(
            chat_id,
            text=(
                "Use os botões do teclado:\n"
                f"• <b>{BTN_AO_VIVO}</b> — receber narração ao vivo\n"
                f"• <b>{BTN_PARAR}</b> — pausar"
            ),
        )

    def poll_updates(self, timeout: int = 25) -> bool:
        """Processa updates. Retorna True se live_requested ficou ativo."""
        if not self.configured:
            return self.live_requested
        try:
            data = self._api(
                "getUpdates",
                offset=self._offset,
                timeout=timeout,
                allowed_updates=["message"],
            )
        except requests.Timeout:
            return self.live_requested
        except Exception:  # noqa: BLE001
            return self.live_requested

        for update in data.get("result") or []:
            uid = update.get("update_id")
            if uid is not None:
                self._offset = int(uid) + 1
            try:
                self._handle_update(update)
            except Exception:  # noqa: BLE001
                continue
        return self.live_requested
