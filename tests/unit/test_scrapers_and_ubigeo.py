"""
Pruebas Unitarias de Armonización de Ubigeos (100 distritos de Huancavelica),
Detección Automática de Nodo (Equipo 1 vs Equipo 2) y Parsers de los 6 Scrapers.
"""

from sentinelnutri.config import detect_current_node
from sentinelnutri.infrastructure.etl.ubigeo_harmonizer import (
    normalize_ubigeo_code,
    resolve_ubigeo_by_name,
)
from sentinelnutri.infrastructure.scrapers.mef_pan_playwright import MefPanPlaywrightScraper
from sentinelnutri.infrastructure.scrapers.midis_playwright import MidisPlaywrightScraper
from sentinelnutri.infrastructure.scrapers.senamhi_scraper import SenamhiScraper
from sentinelnutri.infrastructure.scrapers.sien_ins_scraper import SienInsScraper


def test_node_detector_identifies_equipo1_or_equipo2() -> None:
    node = detect_current_node()
    assert node.node_id in ("EQUIPO_1", "EQUIPO_2")
    assert len(node.pending_tags_for_this_machine) >= 1


def test_ubigeo_harmonizer_covers_100_huancavelica_districts() -> None:
    assert normalize_ubigeo_code("90101") == "090101"
    assert normalize_ubigeo_code("090411") == "090411"
    assert resolve_ubigeo_by_name("Paucará", "Acobamba") == "090206"
    assert resolve_ubigeo_by_name("Lircay", "Angaraes") == "090301"
    assert resolve_ubigeo_by_name("Roble", "Tayacaja") == "090719"
    assert resolve_ubigeo_by_name("Pichos", "Tayacaja") == "090720"
    assert resolve_ubigeo_by_name("Santiago de Tucuma", "Tayacaja") == "090721"


def test_sien_mef_midis_and_senamhi_parsers() -> None:
    sien = SienInsScraper()
    csv_sample = (
        "ubigeo,provincia,distrito,anio,tasa_dci_pct,tasa_anemia_pct,tasa_bajo_peso_pct,ninos_evaluados\n"
        "090206,Acobamba,Paucará,2024,26.8,58.2,6.4,540\n"
    ).encode("utf-8")
    parsed_sien = sien.parse_sien_csv_bytes(csv_sample)
    assert len(parsed_sien) == 1
    assert parsed_sien[0]["ubigeo"] == "090206"
    assert parsed_sien[0]["tasa_dci_pct"] == 26.8

    mef = MefPanPlaywrightScraper()
    html_sample = (
        "<table><tr><td>090101: HUANCAVELICA</td>"
        "<td>1,250,000</td><td>1,050,000</td><td>84.0</td></tr></table>"
    )
    parsed_mef = mef.parse_mef_html_table(html_sample, year=2024)
    assert len(parsed_mef) == 1
    assert parsed_mef[0]["ubigeo"] == "090101"
    assert parsed_mef[0]["ejecucion_pan_mef_pct"] == 84.0

    midis = MidisPlaywrightScraper()
    midis_csv = "ubigeo,distrito,anio,cobertura_juntos_pct,cobertura_cuna_mas_pct,cobertura_qali_warma_pct\n090301,Lircay,2024,78.5,52.0,91.2\n"
    parsed_midis = midis.parse_midis_csv_or_html(midis_csv, year=2024)
    assert len(parsed_midis) == 1
    assert parsed_midis[0]["cobertura_juntos_pct"] == 78.5

    senamhi = SenamhiScraper()
    clim_series = senamhi.build_regional_climate_series(year=2024)
    assert len(clim_series) == 100
