"""Modelos ORM de SQLAlchemy 2.0 equivalentes a `V1__init_msv_schema.sql`."""

from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    """Clase base declarativa para el esquema MSV de SentinelNutri-HVC."""


class CatUbigeoHvcORM(Base):
    __tablename__ = "cat_ubigeo_hvc"

    ubigeo: Mapped[str] = mapped_column(String(6), primary_key=True)
    provincia: Mapped[str] = mapped_column(String(60), nullable=False)
    distrito: Mapped[str] = mapped_column(String(80), nullable=False)
    red_salud: Mapped[str] = mapped_column(String(80), nullable=False)
    altitud_msnm: Mapped[int] = mapped_column(Integer, nullable=False)
    latitud: Mapped[float] = mapped_column(Float, nullable=False)
    longitud: Mapped[float] = mapped_column(Float, nullable=False)
    poblacion_menor_5: Mapped[int] = mapped_column(Integer, nullable=False, default=500)
    ruralidad_pct: Mapped[float] = mapped_column(Float, nullable=False, default=65.0)


class RegistroCargasORM(Base):
    __tablename__ = "registro_cargas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fuente: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    url_origen: Mapped[str] = mapped_column(Text, nullable=False)
    fecha_publicacion_portal: Mapped[str] = mapped_column(String(40), nullable=True)
    fecha_consulta: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utc_now)
    hash_sha256: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    hubo_cambio: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    ruta_archivo_crudo: Mapped[str] = mapped_column(Text, nullable=False)
    registros_procesados: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    estado: Mapped[str] = mapped_column(String(30), nullable=False, default="OK")
    detalle_mensaje: Mapped[str] = mapped_column(Text, nullable=True)


class SerieHistoricaDistritalORM(Base):
    __tablename__ = "serie_historica_distrital"
    __table_args__ = (UniqueConstraint("ubigeo", "anio", "semestre", name="uq_ubigeo_anio_sem"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ubigeo: Mapped[str] = mapped_column(String(6), ForeignKey("cat_ubigeo_hvc.ubigeo"), nullable=False, index=True)
    anio: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    semestre: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    tasa_dci_pct: Mapped[float] = mapped_column(Float, nullable=False)
    tasa_anemia_pct: Mapped[float] = mapped_column(Float, nullable=False)
    tasa_bajo_peso_pct: Mapped[float] = mapped_column(Float, nullable=False)
    ninos_evaluados: Mapped[int] = mapped_column(Integer, nullable=False, default=300)
    pobreza_monetaria_pct: Mapped[float] = mapped_column(Float, nullable=False)
    educacion_materna_secundaria_pct: Mapped[float] = mapped_column(Float, nullable=False)
    agua_cloro_adecuado_pct: Mapped[float] = mapped_column(Float, nullable=False)
    saneamiento_basico_pct: Mapped[float] = mapped_column(Float, nullable=False)
    controles_cred_completo_pct: Mapped[float] = mapped_column(Float, nullable=False)
    lactancia_materna_exclusiva_pct: Mapped[float] = mapped_column(Float, nullable=False)
    ejecucion_pan_mef_pct: Mapped[float] = mapped_column(Float, nullable=False)
    presupuesto_pan_per_capita_soles: Mapped[float] = mapped_column(Float, nullable=False)
    cobertura_juntos_pct: Mapped[float] = mapped_column(Float, nullable=False)
    cobertura_cuna_mas_pct: Mapped[float] = mapped_column(Float, nullable=False)
    cobertura_qali_warma_pct: Mapped[float] = mapped_column(Float, nullable=False)
    dias_heladas_anual: Mapped[int] = mapped_column(Integer, nullable=False)
    temp_minima_promedio_c: Mapped[float] = mapped_column(Float, nullable=False)
    precipitacion_anual_mm: Mapped[float] = mapped_column(Float, nullable=False)
    fecha_actualizacion: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utc_now)


class PrediccionesDciORM(Base):
    __tablename__ = "predicciones_dci"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ubigeo: Mapped[str] = mapped_column(String(6), ForeignKey("cat_ubigeo_hvc.ubigeo"), nullable=False, index=True)
    anio_base: Mapped[int] = mapped_column(Integer, nullable=False)
    horizonte_proyeccion: Mapped[str] = mapped_column(String(20), nullable=False, default="PROXIMO_SEMESTRE")
    dci_actual_pct: Mapped[float] = mapped_column(Float, nullable=False)
    dci_proyectada_pct: Mapped[float] = mapped_column(Float, nullable=False)
    probabilidad_riesgo_critico: Mapped[float] = mapped_column(Float, nullable=False)
    nivel_riesgo: Mapped[str] = mapped_column(String(20), nullable=False)
    supera_umbral_algedonico: Mapped[bool] = mapped_column(Boolean, nullable=False)
    valores_shap_json: Mapped[str] = mapped_column(Text, nullable=False)
    top_factores_riesgo: Mapped[str] = mapped_column(Text, nullable=False)
    version_modelo: Mapped[str] = mapped_column(String(40), nullable=False, default="catboost_shap_v1")
    fecha_prediccion: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utc_now)


class AlertasYRecomendacionesMsvORM(Base):
    __tablename__ = "alertas_y_recomendaciones_msv"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_prediccion: Mapped[int] = mapped_column(Integer, ForeignKey("predicciones_dci.id"), nullable=True)
    ubigeo: Mapped[str] = mapped_column(String(6), ForeignKey("cat_ubigeo_hvc.ubigeo"), nullable=False, index=True)
    provincia: Mapped[str] = mapped_column(String(60), nullable=False)
    nivel_riesgo: Mapped[str] = mapped_column(String(20), nullable=False)
    canal_destino: Mapped[str] = mapped_column(String(30), nullable=False)
    sintesis_narrativa_s4: Mapped[str] = mapped_column(Text, nullable=False)
    recomendacion_salud: Mapped[str] = mapped_column(Text, nullable=False)
    recomendacion_agua_saneamiento: Mapped[str] = mapped_column(Text, nullable=False)
    recomendacion_agricultura_midis: Mapped[str] = mapped_column(Text, nullable=False)
    oei_pei_vinculados: Mapped[str] = mapped_column(String(200), nullable=False)
    ods_vinculados: Mapped[str] = mapped_column(String(100), nullable=False)
    proveedor_llm: Mapped[str] = mapped_column(String(60), nullable=False)
    estado_aprobacion_humana: Mapped[str] = mapped_column(
        String(30), nullable=False, default="PENDIENTE_APROBACION"
    )
    aprobado_por: Mapped[str] = mapped_column(String(80), nullable=True)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utc_now)
    fecha_resolucion: Mapped[datetime] = mapped_column(DateTime, nullable=True)

