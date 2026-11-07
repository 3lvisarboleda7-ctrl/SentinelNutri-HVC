"""
Detector Automático de Nodo Físico (Equipo 1 vs Equipo 2) — Tabla 3 del Perfil de Proyecto.

Permite que tanto el código Python como el agente Antigravity identifiquen de inmediato
en cuál de las dos computadoras se está ejecutando el proyecto, incluso cuando la carpeta
se sincroniza por OneDrive o Git entre ambas máquinas:

- EQUIPO_1 (Estación de Desarrollo):
  Hostname `ELVIS` | Intel Core i7-1355U | Windows 11 Pro | SSD 477 GB.
- EQUIPO_2 (Servidor Local):
  Intel Core i7-7700HQ | GPU NVIDIA GTX 1050 (4 GB) | Windows 10 | SSD 447 GB + HDD 1 TB (`D:\\`).
"""

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import platform
import socket
import subprocess
from typing import Any, Dict, List


@dataclass(frozen=True)
class NodeIdentity:
    """Identidad detectada de la máquina actual."""

    node_id: str  # "EQUIPO_1" o "EQUIPO_2"
    role_name: str
    detection_method: str
    hostname: str
    os_caption: str
    cpu_model: str
    has_nvidia_gtx1050: bool
    has_hdd_d_drive: bool
    recommended_env_file: str
    active_raw_data_dir: str
    active_models_dir: str
    pending_tags_for_this_machine: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _get_windows_cpu_and_os() -> tuple[str, str]:
    """Obtiene el modelo exacto de CPU y edición de Windows sin dependencias externas."""
    cpu_name = platform.processor() or ""
    os_caption = f"{platform.system()} {platform.release()} ({platform.version()})"
    if os.name == "nt":
        try:
            cmd = [
                "powershell",
                "-NoProfile",
                "-Command",
                "[PSCustomObject]@{ CPU=(Get-CimInstance Win32_Processor).Name; OS=(Get-CimInstance Win32_OperatingSystem).Caption } | ConvertTo-Json -Compress",
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=4, check=False)
            if res.returncode == 0 and res.stdout.strip():
                data = json.loads(res.stdout.strip())
                cpu_name = str(data.get("CPU") or cpu_name).strip()
                os_caption = str(data.get("OS") or os_caption).strip()
        except Exception:
            pass
    return cpu_name, os_caption


def _detect_nvidia_gpu() -> tuple[bool, str]:
    """Verifica si existe una GPU NVIDIA (específicamente GTX 1050 en Equipo 2)."""
    try:
        res = subprocess.run(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
        if res.returncode == 0 and res.stdout.strip():
            gpu_name = res.stdout.strip().splitlines()[0]
            return True, gpu_name
    except Exception:
        pass
    return False, "Sin GPU dedicada NVIDIA detectada"


def detect_current_node() -> NodeIdentity:
    """
    Determina automáticamente si la sesión actual corre en el EQUIPO 1 o en el EQUIPO 2.

    Orden de prioridad:
    1. Variable de entorno explícita `NODE_ROLE` o `SENTINEL_NODE_ID` (`EQUIPO_1` / `EQUIPO_2`).
    2. Archivo local `.node_override` (ignorado por Git, solo si se desea forzar manualmente).
    3. Huella de Hardware y Hostname (funciona automáticamente aunque OneDrive sincronice la carpeta):
       - CPU `i7-7700HQ` o GPU `GTX 1050` o ruta `D:/SentinelNutri/hdd` -> `EQUIPO_2`
       - CPU `i7-1355U` o Hostname `ELVIS` o `Windows 11` -> `EQUIPO_1`
    """
    hostname = os.getenv("COMPUTERNAME") or socket.gethostname()
    cpu_model, os_caption = _get_windows_cpu_and_os()
    has_nvidia, gpu_name = _detect_nvidia_gpu()
    has_sentinel_hdd = Path("D:/SentinelNutri/hdd").exists()

    env_override = (os.getenv("SENTINEL_NODE_ID") or os.getenv("NODE_ROLE") or "").upper()
    override_file = Path(".node_override")
    file_override = ""
    if override_file.exists():
        file_override = override_file.read_text(encoding="utf-8").strip().upper()

    node_id = "EQUIPO_1"
    detection_method = "Huella de Hardware/SO por defecto"

    if "EQUIPO_2" in env_override or "LOCAL_SERVER" in env_override:
        node_id = "EQUIPO_2"
        detection_method = "Variable de entorno NODE_ROLE / SENTINEL_NODE_ID"
    elif "EQUIPO_1" in env_override or "DEV_WORKSTATION" in env_override:
        node_id = "EQUIPO_1"
        detection_method = "Variable de entorno NODE_ROLE / SENTINEL_NODE_ID"
    elif file_override in ("EQUIPO_1", "EQUIPO_2"):
        node_id = file_override
        detection_method = "Archivo local .node_override"
    elif "7700HQ" in cpu_model.upper() or "1050" in gpu_name.upper() or has_sentinel_hdd:
        node_id = "EQUIPO_2"
        detection_method = f"Hardware detectado (CPU={cpu_model}, GPU={gpu_name}, HDD_D={has_sentinel_hdd})"
    elif "1355U" in cpu_model.upper() or hostname.upper() == "ELVIS" or "WINDOWS 11" in os_caption.upper():
        node_id = "EQUIPO_1"
        detection_method = f"Hardware/Hostname detectado (Hostname={hostname}, CPU={cpu_model}, SO={os_caption})"

    if node_id == "EQUIPO_2":
        return NodeIdentity(
            node_id="EQUIPO_2",
            role_name="Equipo 2 — Servidor Local (Docker en SSD + HDD 1TB + Ollama GTX 1050 + Cloudflare Tunnel)",
            detection_method=detection_method,
            hostname=hostname,
            os_caption=os_caption,
            cpu_model=f"{cpu_model} | GPU: {gpu_name}",
            has_nvidia_gtx1050=has_nvidia,
            has_hdd_d_drive=Path("D:/").exists(),
            recommended_env_file="config/.env.equipo2.example",
            active_raw_data_dir=os.getenv("RAW_DATA_DIR", "D:/SentinelNutri/hdd/raw"),
            active_models_dir=os.getenv("MODELS_DIR", "D:/SentinelNutri/hdd/models"),
            pending_tags_for_this_machine=["[EQUIPO 2]"],
        )

    return NodeIdentity(
        node_id="EQUIPO_1",
        role_name="Equipo 1 — Estación de Desarrollo (VS Code + Pruebas + Google Colab)",
        detection_method=detection_method,
        hostname=hostname,
        os_caption=os_caption,
        cpu_model=f"{cpu_model} | GPU: {gpu_name}",
        has_nvidia_gtx1050=has_nvidia,
        has_hdd_d_drive=Path("D:/").exists(),
        recommended_env_file="config/.env.equipo1.example",
        active_raw_data_dir=os.getenv("RAW_DATA_DIR", "./data/raw"),
        active_models_dir=os.getenv("MODELS_DIR", "./data/models"),
        pending_tags_for_this_machine=["[EQUIPO 1]", "[EQUIPO 1 -> COLAB]"],
    )

