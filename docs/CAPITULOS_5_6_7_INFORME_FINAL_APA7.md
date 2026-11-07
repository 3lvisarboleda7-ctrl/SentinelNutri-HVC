# Capítulos 5, 6 y 7 del Informe Final (Formato APA 7) — SentinelNutri-HVC

**Proyecto:** SentinelNutri-HVC: Sistema Inteligente de Alerta Temprana para el Sistema 4 del MSV, Región Huancavelica  
**Curso:** Modelo de Sistema Viable (MSV) — FIIS UNI  
**Autor:** Elvis Arboleda  
**Docente:** Ing. Ricardo Rodríguez-Ulloa  

---

## Capítulo 5. Implementación Cibernética del Sistema 4 y Mecanismos de Variedad (Ley de Ashby)

### 5.1. Materialización del Atenuador y del Amplificador de Variedad

De acuerdo con la Ley de la Variedad Requerida de Ashby (1956) y el Modelo de Sistema Viable de Beer (1972, 1979), la viabilidad del Gobierno Regional de Huancavelica frente al problema crónico de la desnutrición crónica infantil (DCI, $20,3\,\%$ regional frente al $12,1\,\%$ nacional) exige equilibrar la variedad ambiental de los **100 distritos** de sus **7 provincias** con la capacidad de respuesta de la Gerencia Regional de Desarrollo Social (**S3**) y del Consejo Regional (**S5**).

El sistema **SentinelNutri-HVC** materializa este equilibrio mediante dos mecanismos cibernéticos complementarios desplegados en una infraestructura dual de costo cero (**Equipo 1: Estación de Desarrollo** y **Equipo 2: Servidor Local con SSD + HDD de 1 TB + GPU GTX 1050**):

1. **Atenuador de Variedad Ambiental (`CatBoost + SHAP`):** Filtra y comprime `1 100` registros históricos distritales (`2014–2024`, 100 distritos $\times$ 11 años) distribuidos en cinco dimensiones (antropométrica/nutricional, socioeconómica, acceso a servicios de agua y salud, ejecución presupuestal del Programa Articulado Nutricional `0001` / programas MIDIS y régimen climático de heladas del SENAMHI) en una probabilidad calibrada de riesgo crítico y una tasa proyectada de DCI por distrito.
2. **Amplificador de Variedad de Gestión (Agente Supervisor en `n8n` + LLM con Reglas Fijas):** Transforma las predicciones y los valores SHAP en informes ejecutivos y recomendaciones diferenciadas por provincia y sector (**Salud/DIRESA**, **Agua y Saneamiento/DRVCS**, **Agricultura/MIDIS/MEF**) alineadas a los Objetivos Estratégicos Institucionales (**OEI**) del **PEI 2020–2027 Ampliado** del GORE Huancavelica.

### 5.2. Las 6 Herramientas del Agente Supervisor y las 3 Reglas Fijas Cibernéticas

Siguiendo las recomendaciones de gobernanza de inteligencia artificial para el sector público de la CEPAL (Clavijo, 2026), el Agente Supervisor (`AI Agent` en `n8n`) dispone de **6 herramientas** (`extraer_fuentes`, `consultar_bd`, `predecir_riesgo`, `explicar_riesgo`, `redactar_informe` y `notificar`), pero **tres decisiones críticas permanecen en Reglas Fijas deterministas** fuera del alcance del modelo de lenguaje:

- **Regla Fija 1 (Inferencia Numérica Determinista):** La proyección de DCI y la probabilidad de riesgo las calcula exclusivamente el motor `CatBoost` (`/predict`), evitando cualquier alucinación numérica del LLM.
- **Regla Fija 2 (Canal Algedónico Automatizado $\text{S1/S4} \rightarrow \text{S5}$):** Un nodo condicional fijo (`IF`) evalúa si la DCI proyectada supera el umbral crítico del **$25,0\,\%$**. Cuando se supera, la señal algedónica se envía de inmediato al **Sistema 5 (Consejo Regional / Gobernación)** por Telegram y Gmail sin que el LLM pueda omitirla ni retrasarla.
- **Regla Fija 3 (Aprobación Humana en el Canal de Control $\text{S4} \rightarrow \text{S3}$):** Toda recomendación dirigida al **Sistema 3 (Gerencia Regional de Desarrollo Social)** permanece en estado `PENDIENTE_APROBACION` hasta que el responsable humano la aprueba desde su celular a través del enlace HTTPS seguro publicado mediante **Cloudflare Tunnel** (sin abrir puertos en el router del Equipo 2 con Windows 10).

---

## Capítulo 6. Evaluación del Desempeño Predictivo y Explicabilidad XAI (Soporte a S3*)

### 6.1. Validación Cruzada Estratificada del Motor Predictivo (`2014–2024`)

La validación del motor predictivo sobre el panel histórico integrado de los **100 distritos de Huancavelica (`2014–2024`, $N = 1\,100$ observaciones distritales-anuales)** superó la meta académica de referencia ($\text{AUC-ROC} \ge 0,90$) establecida por Navarro-Guillén et al. (2026) para vigilancia nutricional sobre registros del SIEN en el Perú.

**Tabla 1**  
*Métricas Globales de Desempeño del Motor Predictivo CatBoost + SHAP (Validación 2014–2024, $N = 1\,100$)*

| Métrica de Evaluación | Valor Obtenido | Meta de Referencia (Navarro-Guillén et al., 2026) | Estado de Cumplimiento |
| :--- | :---: | :---: | :---: |
| **Área Bajo la Curva ROC ($\text{AUC-ROC}$)** | **$0,9993$** | $\ge 0,9000$ | **Cumple ($+0,0993$)** |
| **Puntaje $\text{F1-Score}$** | **$0,8917$** | $\ge 0,8500$ | **Cumple** |
| **Sensibilidad (*Recall* en distritos críticos)** | **$1,0000$** | $\ge 0,9000$ | **Cumple ($0$ falsos negativos)** |
| **Precisión (*Precision*)** | **$0,8046$** | $\ge 0,8000$ | **Cumple** |
| **Exactitud Global (*Accuracy*)** | **$91,55\,\%$** | $\ge 85,00\,\%$ | **Cumple** |

*Nota.* Matriz de confusión sobre $N = 1\,100$: Verdaderos Positivos ($\text{TP} = 383$), Verdaderos Negativos ($\text{TN} = 624$), Falsos Positivos ($\text{FP} = 93$), Falsos Negativos ($\text{FN} = 0$). La ausencia de falsos negativos ($\text{FN} = 0$) garantiza que ningún distrito en riesgo crítico quede sin alerta temprana. La curva ROC correspondiente se presenta en [`docs/figures/fig1_roc_cv5_catboost_hvc.png`](file:///c:/Users/arbol/OneDrive/Univesidad_Nacional_de_Ingenieria/Ciclo_8/MSV/SentinelNutri-HVC/docs/figures/fig1_roc_cv5_catboost_hvc.png).

**Tabla 2**  
*Desempeño y Estado del Homeostato S3–S4 por Provincia y Red de Salud (Coordinación S2, Corte 2024)*

| Provincia (Red de Salud S2) | Distritos Monitoreados | Exactitud Provincial (%) | DCI Actual Promedio S3 (%) | DCI Proyectada Promedio S4 (%) | Distritos en Alerta Algedónica S5 ($> 25\,\%$) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Acobamba** | 8 | $95,45\,\%$ | $18,62\,\%$ | $18,17\,\%$ | 0 |
| **Angaraes** | 12 | $93,94\,\%$ | $18,70\,\%$ | $18,30\,\%$ | 1 |
| **Castrovirreyna** | 13 | $90,21\,\%$ | $16,35\,\%$ | $15,45\,\%$ | 1 |
| **Churcampa** | 11 | $91,74\,\%$ | $16,82\,\%$ | $15,95\,\%$ | 0 |
| **Huancavelica** | 19 | $86,60\,\%$ | $17,09\,\%$ | $16,41\,\%$ | 1 |
| **Huaytará** | 16 | $92,05\,\%$ | $17,99\,\%$ | $17,34\,\%$ | 2 |
| **Tayacaja** | 21 | $93,51\,\%$ | $16,54\,\%$ | $15,63\,\%$ | 0 |
| **Total / Promedio Regional** | **100** | **$91,55\,\%$** | **$17,26\,\%$** | **$16,53\,\%$** | **5** |

*Nota.* El gráfico comparativo del Homeostato S3–S4 para las 7 provincias se encuentra exportado en 300 DPI en [`docs/figures/fig4_homeostato_s3_s4_7_provincias.png`](file:///c:/Users/arbol/OneDrive/Univesidad_Nacional_de_Ingenieria/Ciclo_8/MSV/SentinelNutri-HVC/docs/figures/fig4_homeostato_s3_s4_7_provincias.png).

---

### 6.2. Auditoría de Explicabilidad XAI mediante Valores SHAP (Soporte a S3*)

Para evitar que el modelo opere como una «caja negra» y fortalecer el canal de **Auditoría ($\text{S3}^*$)** del MSV, la herramienta `explicar_riesgo` descompone cada proyección distrital utilizando valores de Shapley (`SHAP`).

**Tabla 3**  
*Ranking Global de Importancia de Variables según Impacto Medio Absoluto $|\text{SHAP}|$ (Auditoría S3\*)*

| Orden | Variable del Modelo | Dimensión / Fuente Oficial | Impacto Medio $\|\text{SHAP}\|$ (puntos %) | Vinculación OEI (PEI 2020–2027) |
| :---: | :--- | :--- | :---: | :--- |
| 1 | `tasa_dci_pct` | 1. Antropométrica (SIEN-HIS INS/CENAN) | $2,4515$ | **OEI.01** (Salud materno-infantil) |
| 2 | `agua_cloro_adecuado_pct` | 3. Acceso a Servicios (ENDES INEI) | $1,1306$ | **OEI.04** (Agua segura y saneamiento rural) |
| 3 | `dias_heladas_anual` | 5. Climática (SENAMHI) | $1,0904$ | **OEI.10** (Gestión del riesgo de desastres) |
| 4 | `pobreza_monetaria_pct` | 2. Socioeconómica (INEI Mapa Pobreza) | $0,8501$ | **OEI.08** (Competitividad agropecuaria) |
| 5 | `ejecucion_pan_mef_pct` | 4. Presupuesto Público (MEF PAN 0001) | $0,5971$ | **OEI.03** (Gestión pública moderna) |
| 6 | `controles_cred_completo_pct` | 3. Acceso a Salud (ENDES INEI) | $0,4809$ | **OEI.01** (Controles CRED completos) |
| 7 | `tasa_anemia_pct` | 1. Nutricional (SIEN-HIS INS/CENAN) | $0,4395$ | **OEI.01** (Reducción de anemia 6–35 m) |
| 8 | `cobertura_cuna_mas_pct` | 4. Programas Sociales (MIDIS) | $0,3646$ | **OEI.01 / OEI.03** (Articulación S2) |
| 9 | `educacion_materna_secundaria_pct` | 2. Socioeconómica (ENDES INEI) | $0,2896$ | **OEI.02** (Educación básica de calidad) |
| 10 | `cobertura_juntos_pct` | 4. Programas Sociales (MIDIS) | $0,2691$ | **OEI.01 / OEI.03** (Protección social) |

*Nota.* El gráfico global de importancia SHAP se encuentra en [`docs/figures/fig2_shap_importancia_global_s3_star.png`](file:///c:/Users/arbol/OneDrive/Univesidad_Nacional_de_Ingenieria/Ciclo_8/MSV/SentinelNutri-HVC/docs/figures/fig2_shap_importancia_global_s3_star.png) y la descomposición local (*Waterfall*) del distrito más crítico (`090411 Santa Ana`, Castrovirreyna, $\text{DCI proyectada} = 29,29\,\%$) en [`docs/figures/fig3_shap_waterfall_distrito_critico.png`](file:///c:/Users/arbol/OneDrive/Univesidad_Nacional_de_Ingenieria/Ciclo_8/MSV/SentinelNutri-HVC/docs/figures/fig3_shap_waterfall_distrito_critico.png).

---

## Capítulo 7. Gobernanza Cibernética, Cumplimiento de la Ley N.º 29733 y Articulación con el PEI y los ODS

### 7.1. Distritos Críticos que Disparan el Canal Algedónico Automatizado ($\text{S1/S4} \rightarrow \text{S5}$)

En el corte de evaluación `2024–2025`, la **Regla Fija 2** (`DCI proyectada > 25,0 %`) identificó **5 distritos en alerta algedónica crítica**, elevando la señal de forma inmediata al **Sistema 5 (Consejo Regional)** sin posibilidad de omisión por parte del LLM:

**Tabla 4**  
*Distritos de Huancavelica que Activan el Canal Algedónico Automatizado hacia el Sistema 5 ($\text{DCI Proyectada} > 25,0\,\%$)*

| Ubigeo | Provincia | Distrito | DCI Actual S3 (%) | DCI Proyectada S4 (%) | Canal MSV Activado | Determinante Principal SHAP ($\text{S3}^*$) |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- |
| `090411` | Castrovirreyna | **Santa Ana** | $27,50\,\%$ | **$29,29\,\%$** | `S5_ALGEDONICO` | Inercia DCI previa + Heladas altoandinas (`4 469 msnm`) |
| `090612` | Huaytará | **San Antonio de Cusicancha** | $26,80\,\%$ | **$27,13\,\%$** | `S5_ALGEDONICO` | Baja cobertura de agua clorada + Heladas |
| `090609` | Huaytará | **Pilpichaca** | $26,50\,\%$ | **$27,04\,\%$** | `S5_ALGEDONICO` | Altitud extrema (`4 092 msnm`, $118$ días de heladas) |
| `090304` | Angaraes | **Ccochaccasa** | $26,20\,\%$ | **$26,16\,\%$** | `S5_ALGEDONICO` | Baja cloración de agua rural + Heladas (`4 150 msnm`) |
| `090102` | Huancavelica | **Acobambilla** | $25,40\,\%$ | **$25,08\,\%$** | `S5_ALGEDONICO` | Brecha en controles CRED y agua segura |

---

### 7.2. Verificación Técnica de Ética y Privacidad de Datos (Ley N.º 29733)

1. **Cumplimiento de la Ley N.º 29733 (Protección de Datos Personales):** El módulo [`privacy_guard.py`](file:///c:/Users/arbol/OneDrive/Univesidad_Nacional_de_Ingenieria/Ciclo_8/MSV/SentinelNutri-HVC/src/sentinelnutri/domain/rules/privacy_guard.py) inspecciona recursivamente todo diccionario antes de invocar la herramienta `redactar_informe` hacia la API de Gemini u Ollama. Si detecta cualquier campo nominal (`dni`, `nombres`, `apellidos`, `historia_clinica`, `direccion`, `fecha_nacimiento_exacta`), bloquea la solicitud lanzando `PrivacyViolationError` (`HTTP 422`), garantizando por código que hacia los proveedores de LLM solo viajen indicadores agregados por distrito.
2. **Extracción Responsable y Trazabilidad `SHA-256`:** El módulo [`scraping_ethics.py`](file:///c:/Users/arbol/OneDrive/Univesidad_Nacional_de_Ingenieria/Ciclo_8/MSV/SentinelNutri-HVC/src/sentinelnutri/domain/rules/scraping_ethics.py) valida el archivo `robots.txt` de cada portal estatal, identifica las peticiones con el encabezado académico `SentinelNutri-HVC/1.0 (Proyecto Academico FIIS-UNI; MSV-S4)` y registra en la tabla `registro_cargas` de PostgreSQL la huella digital `SHA-256` de cada archivo descargado para procesar únicamente aquello que cambió.

---

### 7.3. Articulación con el PEI 2020–2027 del GORE Huancavelica y los ODS 2, 3 y 6

La matriz completa de los 100 distritos exportada en [`data/exports/matriz_gobernanza_oei_ods_hvc.csv`](file:///c:/Users/arbol/OneDrive/Univesidad_Nacional_de_Ingenieria/Ciclo_8/MSV/SentinelNutri-HVC/data/exports/matriz_gobernanza_oei_ods_hvc.csv) vincula cada alerta y recomendación sectorial del **Sistema 4** con los instrumentos estratégicos regionales y globales:

- **ODS 2 (Hambre Cero — Meta 2.2) $\leftrightarrow$ OEI.01 y OEI.08 del PEI 2020–2027:** Erradicación de la desnutrición crónica y anemia en menores de 5 años mediante focalización temprana de controles CRED, suplementación preventiva de hierro y protección de la agricultura familiar altoandina.
- **ODS 3 (Salud y Bienestar — Meta 3.2) $\leftrightarrow$ OEI.01 y OEI.03 del PEI 2020–2027:** Coordinación interprovincial (**S2**) de las 7 Redes de Salud de la DIRESA Huancavelica y mejora de la calidad de ejecución del Programa Articulado Nutricional (`0001`).
- **ODS 6 (Agua Limpia y Saneamiento — Meta 6.1) $\leftrightarrow$ OEI.04 del PEI 2020–2027:** Intervención prioritaria sobre los sistemas de cloración rural (donde los valores SHAP demuestran el segundo mayor impacto estructural sobre la DCI regional, $|\text{SHAP}| = 1,1306$ puntos porcentuales).

