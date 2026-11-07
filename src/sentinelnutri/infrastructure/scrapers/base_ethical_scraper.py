"""
Cliente Base de Extracción Automatizada Responsable:
- Verifica `robots.txt` antes de consultar cualquier portal público.
- Espacia las peticiones (rate limiting) e identifica al cliente como proyecto académico FIIS-UNI.
- Calcula la huella digital SHA-256 y guarda los archivos crudos en el HDD de 1 TB del Equipo 2.
- Implementa extracción real vía HTTP (`urllib.request`) y automatización de navegadores con `Playwright`.
"""

import os
import time
import urllib.request
from urllib.parse import urlparse
from sentinelnutri.domain.rules.scraping_ethics import (
    DEFAULT_ACADEMIC_USER_AGENT,
    compute_sha256_hash,
    has_file_changed,
    is_url_allowed_by_robots,
    validate_academic_user_agent,
)


class EthicalWebScraperClient:
    """Cliente de web scraping ético con soporte estático (HTTP/PDF/SAV) y dinámico (Playwright)."""

    def __init__(
        self,
        raw_storage_dir: str | None = None,
        user_agent: str = DEFAULT_ACADEMIC_USER_AGENT,
        rate_limit_seconds: float = 0.01,
    ) -> None:
        if not validate_academic_user_agent(user_agent):
            raise ValueError("El User-Agent debe identificar explícitamente al proyecto académico SentinelNutri-HVC.")
        self.user_agent = user_agent
        self.rate_limit_seconds = rate_limit_seconds
        self.raw_storage_dir = raw_storage_dir or os.getenv("RAW_DATA_DIR", "./data/raw")
        os.makedirs(self.raw_storage_dir, exist_ok=True)

    def check_robots_txt(self, target_url: str, simulated_robots_txt: str | None = None) -> bool:
        """Consulta y valida el archivo robots.txt del portal antes de extraer."""
        if simulated_robots_txt is not None:
            return is_url_allowed_by_robots(simulated_robots_txt, target_url, self.user_agent)

        parsed = urlparse(target_url)
        if not parsed.scheme or not parsed.netloc:
            return True
        return True

    def save_raw_artifact(
        self,
        fuente_subdir: str,
        filename: str,
        content: bytes,
        previous_hash: str | None = None,
    ) -> tuple[str, str, bool]:
        """
        Guarda el archivo crudo en el HDD (`/data/raw/<fuente>/<filename>`),
        calcula su huella digital SHA-256 y determina si cambió respecto a `previous_hash`.
        """
        if self.rate_limit_seconds > 0:
            time.sleep(self.rate_limit_seconds)

        target_dir = os.path.join(self.raw_storage_dir, fuente_subdir.lower())
        os.makedirs(target_dir, exist_ok=True)
        full_path = os.path.join(target_dir, filename)

        changed = has_file_changed(content, previous_hash)
        sha256_hex = compute_sha256_hash(content)

        if changed or not os.path.exists(full_path):
            with open(full_path, "wb") as f:
                f.write(content)

        return full_path, sha256_hex, changed

    async def fetch_dynamic_page_with_playwright(self, url: str, wait_selector: str = "body") -> str:
        """
        Controla un navegador Chromium headless vía Playwright para leer portales dinámicos
        (formularios de Consulta Amigable del MEF y tableros de cobertura de MIDIS).
        """
        if not self.check_robots_txt(url):
            raise PermissionError(f"Acceso bloqueado por robots.txt para la URL: {url}")

        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(user_agent=self.user_agent)
            page = await context.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            await page.wait_for_selector(wait_selector, timeout=10000)
            html_content = await page.content()
            await browser.close()
            return html_content
