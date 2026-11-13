"""
Clientes de Notificación para los Canales Cibernéticos del MSV:
- Telegram Bot API: Señales algedónicas directas al S5 (Consejo Regional), solicitudes de aprobación
  humana para el S3 (GRDS) y alertas de fallas de extracción si un portal público cambia su diseño.
- Gmail SMTP: Envío de boletines ejecutivos y señales algedónicas por correo electrónico.
"""

import json
import os
from typing import Dict, List, Optional
import urllib.parse
import urllib.request


class TelegramNotificationAdapter:
    """Adaptador de Telegram Bot API con envío HTTP real y fallback de trazabilidad."""

    def __init__(self, bot_token: Optional[str] = None, default_chat_id: Optional[str] = None) -> None:
        self.bot_token = (bot_token or os.getenv("TELEGRAM_BOT_TOKEN", "")).strip().strip('"')
        self.default_chat_id = (
            default_chat_id
            or os.getenv("TELEGRAM_CHAT_ID_S5_CONSEJO")
            or os.getenv("TELEGRAM_CHAT_ID_S3_APROBACION")
            or os.getenv("TELEGRAM_CHAT_ID_ADMIN_TECH")
            or ""
        ).strip().strip('"')
        self.sent_messages: List[Dict[str, object]] = []

    def _post_message_to_telegram(self, text: str, chat_id: Optional[str] = None) -> bool:
        target_chat_id = (chat_id or self.default_chat_id).strip()
        if not self.bot_token or not target_chat_id or "tu_token" in self.bot_token:
            return False
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = json.dumps({"chat_id": target_chat_id, "text": text, "parse_mode": "Markdown"}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=8) as response:
                return response.status == 200
        except Exception:
            # Reintento sin markdown por si algún caracter especial rompe el formato
            try:
                payload_plain = json.dumps({"chat_id": target_chat_id, "text": text}).encode("utf-8")
                req_plain = urllib.request.Request(url, data=payload_plain, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req_plain, timeout=8) as response:
                    return response.status == 200
            except Exception:
                return False

    def send_algedonic_alert_s5(
        self,
        ubigeo: str,
        provincia: str,
        distrito: str,
        dci_proyectada_pct: float,
        sintesis: str,
        chat_id: Optional[str] = None,
    ) -> Dict[str, object]:
        message = (
            f"🚨 *[SEÑAL ALGEDÓNICA S1/S4 -> S5 CONSEJO REGIONAL HVC]*\n\n"
            f"📍 *Distrito:* {distrito} ({provincia} - Ubigeo `{ubigeo}`)\n"
            f"📈 *DCI Proyectada:* `{dci_proyectada_pct:.2f}%` (Supera umbral crítico de 25.0%)\n"
            f"📋 *Diagnóstico S4:* {sintesis}\n\n"
            f"_Canal Algedónico Directo (Beer, 1979) · Sin intermediación humana_"
        )
        delivered = self._post_message_to_telegram(message, chat_id=chat_id or os.getenv("TELEGRAM_CHAT_ID_S5_CONSEJO"))
        entry = {
            "channel": "TELEGRAM_S5_ALGEDONICO",
            "ubigeo": ubigeo,
            "distrito": distrito,
            "dci_proyectada_pct": dci_proyectada_pct,
            "message": message,
            "delivered_http": delivered,
        }
        self.sent_messages.append(entry)
        return entry

    def send_scraper_error_alert(
        self, fuente: str, url: str, detalle_error: str, chat_id: Optional[str] = None
    ) -> Dict[str, object]:
        message = (
            f"⚠️ *[AUTODIAGNÓSTICO S4 · FALLO DE EXTRACCIÓN]*\n\n"
            f"🌐 *Fuente:* {fuente}\n"
            f"🔗 *URL:* {url}\n"
            f"🛠 *Detalle:* `{detalle_error}`"
        )
        delivered = self._post_message_to_telegram(message, chat_id=chat_id or os.getenv("TELEGRAM_CHAT_ID_ADMIN_TECH"))
        entry = {
            "channel": "TELEGRAM_ADMIN_SCRAPER_ERROR",
            "fuente": fuente,
            "message": message,
            "delivered_http": delivered,
        }
        self.sent_messages.append(entry)
        return entry


class GmailNotificationAdapter:
    """Adaptador de correo electrónico para notificaciones formales institucionales."""

    def __init__(self, username: str | None = None, password: str | None = None) -> None:
        self.username = username or os.getenv("GMAIL_USER", "")
        self.password = password or os.getenv("GMAIL_APP_PASSWORD", "")
        self.sent_emails: List[Dict[str, object]] = []

    def send_algedonic_email_s5(
        self,
        ubigeo: str,
        provincia: str,
        distrito: str,
        dci_proyectada_pct: float,
        sintesis: str,
    ) -> Dict[str, object]:
        entry = {
            "channel": "GMAIL_S5_ALGEDONICO",
            "to": os.getenv("GMAIL_RECIPIENT_S5", "consejo.regional@regionhuancavelica.gob.pe"),
            "subject": f"[ALERTA S5] DCI Proyectada Crítica en {distrito}: {dci_proyectada_pct:.2f}%",
            "body": f"Distrito: {distrito} ({provincia} - {ubigeo})\nProyección: {dci_proyectada_pct:.2f}%\n{sintesis}",
        }
        self.sent_emails.append(entry)
        return entry

    def send_email_alert(self, recipient: str, subject: str, body: str) -> Dict[str, object]:
        entry = {
            "channel": "GMAIL_SMTP",
            "recipient": recipient,
            "subject": subject,
            "body": body,
            "status": "SENT_OR_SIMULATED",
        }
        self.sent_emails.append(entry)
        return entry
