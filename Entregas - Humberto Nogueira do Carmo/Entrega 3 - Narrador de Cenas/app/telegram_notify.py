"""Cliente Telegram para avisos de monitoramento de cenas."""

from __future__ import annotations

import os
from typing import Optional

import requests


class TelegramNotifier:
    def __init__(
        self,
        bot_token: Optional[str] = None,
        chat_id: Optional[str] = None,
    ):
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID", "")

    @property
    def configured(self) -> bool:
        return bool(self.bot_token and self.chat_id)

    def send_message(self, text: str, parse_mode: str = "HTML") -> dict:
        if not self.configured:
            raise RuntimeError(
                "Telegram não configurado. Defina TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID."
            )

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text[:4000],
            "parse_mode": parse_mode,
            "disable_web_page_preview": True,
        }
        resp = requests.post(url, json=payload, timeout=20)
        resp.raise_for_status()
        return resp.json()

    def send_scene_alert(self, summary: str, video_name: str = "") -> dict:
        header = "🎬 <b>Monitoramento de cena</b>"
        if video_name:
            header += f"\n📁 <code>{video_name}</code>"
        body = f"{header}\n\n{summary}"
        return self.send_message(body)
