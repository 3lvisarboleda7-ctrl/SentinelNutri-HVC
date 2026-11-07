"""
Herramienta 1 del Agente Supervisor: `extraer_fuentes` (Tabla 5).
Revisa los portales públicos (SIEN-HIS, ENDES, INEI, MEF, MIDIS, SENAMHI),
detecta publicaciones nuevas por fecha y hash SHA-256, las descarga al HDD del Equipo 2
e integra las series por ubigeo distrital en PostgreSQL.
"""

from typing import Dict, Optional
from sentinelnutri.domain.ports.repository_port import RepositoryPort
from sentinelnutri.domain.ports.scraper_port import ScraperPort


class Tool1ExtraerFuentesUseCase:
    """Caso de uso para la extracción automatizada (backfill 2014-2024 y vigilancia semanal)."""

    def __init__(self, repository: RepositoryPort, scraper_orchestrator: ScraperPort) -> None:
        self._repo = repository
        self._scraper = scraper_orchestrator

    def execute(
        self,
        mode: str = "weekly_watch",
        start_year: int = 2014,
        end_year: int = 2024,
        force_rebuild: bool = False,
    ) -> Dict[str, object]:
        """
        Ejecuta la revisión de los portales públicos:
        - `mode="backfill"`: busca y descarga la serie histórica 2014-2024 completa.
        - `mode="weekly_watch"`: compara fecha y hash SHA-256 contra PostgreSQL y procesa solo cambios.
        """
        scrape_results = self._scraper.execute_extraction(
            mode=mode,
            start_year=start_year,
            end_year=end_year,
        )

        any_changed = force_rebuild
        broken_portals = []
        registered_logs = []

        for res in scrape_results:
            log_entry = self._repo.register_load_attempt(
                fuente=res.fuente,
                url_origen=res.url_origen,
                hash_sha256=res.hash_sha256,
                hubo_cambio=res.hubo_cambio,
                ruta_archivo_crudo=res.ruta_archivo_crudo,
                registros_procesados=res.registros_extraidos,
                estado=res.estado,
                detalle_mensaje=res.mensaje,
            )
            registered_logs.append(log_entry)
            if res.hubo_cambio:
                any_changed = True
            if res.estado == "ERROR_DISENO_PORTAL":
                broken_portals.append({"fuente": res.fuente, "url": res.url_origen, "error": res.mensaje})

        records_upserted = 0
        if any_changed or mode == "backfill":
            integrated_records = self._scraper.build_integrated_records(
                start_year=start_year,
                end_year=end_year,
            )
            records_upserted = self._repo.upsert_historical_records(integrated_records)

        return {
            "tool": "extraer_fuentes",
            "mode": mode,
            "periodo": f"{start_year}-{end_year}",
            "portales_consultados": len(scrape_results),
            "hubo_publicaciones_nuevas": any_changed,
            "registros_distritales_integrados": records_upserted,
            "fallos_extraccion_detectados": broken_portals,
            "detalle_fuentes": [
                {
                    "fuente": r.fuente,
                    "fecha_publicacion": r.fecha_publicacion,
                    "hash_sha256": r.hash_sha256[:16] + "...",
                    "hubo_cambio": r.hubo_cambio,
                    "estado": r.estado,
                    "ruta_hdd": r.ruta_archivo_crudo,
                }
                for r in scrape_results
            ],
        }

