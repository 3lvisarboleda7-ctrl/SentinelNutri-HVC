"""
Clientes de Notificación para los Canales Cibernéticos del MSV:
- Telegram Bot API: Señales algedónicas directas al S5 (Consejo Regional), solicitudes de aprobación
  humana para el S3 (GRDS) y alertas de fallas de extracción si un portal público cambia su diseño.
- Gmail SMTP: Envío de boletines ejecutivos y señales algedónicas por correo electrónico.
"""

import os
from typing import Dict, List


class TelegramNotificationAdapter:
    """Adaptador de Telegram Bot API con registro en memoria para trazabilidad y pruebas."""

    def __init__(self, bot_token: str | None = None) -> None:
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.sent_messages: List[Dict[str, object]] = []

    def send_algedonic_alert_s5(
        self,
        ubigeo: str,
        provincia: str,
        distrito: str,
        dci_proyectada_pct: float,
        sintesis: str,
    ) -> Dict[str, object]:
        message = (
            f"🚨 [SEÑAL ALGEDÓNICA S1/S4 -> S5 CONSEJO REGIONAL HVC]\n"
            f"Distrito: {distrito} ({provincia} - Ubigeo {ubigeo})\n"
            f"DCI Proyectada: {dci_proyectada_pct:.2f}% (Supera umbral fijo de 25.0%)\n"
            f"Diagnóstico S4: {sintesis}"
        )
        entry = {
            "channel": "TELEGRAM_S5_ALGEDONICO",
            "ubigeo": ubigeo,
            "distrito": distrito,
            "dci_proyectada_pct": dci_proyectada_pct,
            "message": message,
        }
        self.sent_messages.append(entry)
        return entry

    def send_scraper_error_alert(self, fuente: str, url: str, detalle_error: str) -> Dict[str, object]:
        message = (
            f"⚠️ [AUTODIAGNÓSTICO S4 · FALLO DE EXTRACCIÓN]\n"
            f"Fuente: {fuente}\nURL: {url}\nDetalle: {detalle_error}"
        )
        entry = {"channel": "TELEGRAM_ADMIN_SCRAPER_ERROR", "fuente": fuente, "message": message}
        self.sent_messages.append(entry)
        return entry


class GmailNotificationAdapter:
    """Adaptador de correo electrónico Gmail para señales algedónicas S5 y aprobación humana S3."""

    def __init__(self) -> None:
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
            "subject": f"[URGENTE - CANAL ALGEDÓNICO S5] Riesgo Crítico DCI ({dci_proyectada_pct:.1f}%) en {distrito}",
            "body": sintesis,
        }
        self.sent_emails.append(entry)
        return entry

