# Capítulos 5, 6 y 7 del Informe Final (Formato APA 7) — SentinelNutri-HVC

**Proyecto:** SentinelNutri-HVC: Sistema Inteligente de Alerta Temprana para el Sistema 4 del MSV, Región Huancavelica  
**Curso:** Modelo de Sistema Viable (MSV) — FIIS UNI  
**Autor:** Elvis Arboleda  
**Docente:** Ing. Ricardo Rodríguez-Ulloa  
**Corte de avance técnico:** 12 de noviembre de 2026 (commits sincronizados hasta `165e0ee`)  

---

## Capítulo 5. Implementación Cibernética del Sistema 4 y Mecanismos de Variedad (Ley de Ashby)

### 5.1. Materialización del Atenuador y del Amplificador de Variedad

De acuerdo con la Ley de la Variedad Requerida de Ashby (1956) y el Modelo de Sistema Viable de Beer (1972, 1979), la viabilidad del Gobierno Regional de Huancavelica frente al problema crónico de la desnutrición crónica infantil (DCI, $20,3\,\%$ de línea base regional frente al $12,1\,\%$ nacional) exige equilibrar la variedad ambiental de los **100 distritos** de sus **7 provincias** con la capacidad de respuesta de la Gerencia Regional de Desarrollo Social (**S3**) y del Consejo Regional (**S5**).

El sistema **SentinelNutri-HVC** materializa este equilibrio mediante dos mecanismos cibernéticos complementarios desplegados en una infraestructura dual de costo cero (**Equipo 1: Estación de Desarrollo Windows 11 + Google Colab** y **Equipo 2: Servidor Local Windows 10 con Docker en SSD `C:\SentinelNutri\ssd`, almacén en HDD 1 TB `D:\SentinelNutri\hdd` y GPU NVIDIA GTX 1050 de 4 GB**):

1. **Atenuador de Variedad Ambiental (`CatBoost + SHAP`):** Comprime `1 100` registros históricos distritales (`2014–2024`, $100\text{ distritos} \times 11\text{ años}$, $26$ variables en la matriz consolidada) distribuidos en cinco dimensiones —antropométrica/nutricional, socioeconómica, acceso a servicios de agua y salud, ejecución presupuestal del Programa Articulado Nutricional `0001` / programas MIDIS y régimen climático de heladas del SENAMHI— en una probabilidad calibrada de riesgo crítico y una tasa proyectada de DCI por distrito. El modelo entrenado (`catboost_dci_hvc.cbm`, $364\,624\text{ bytes}$) se aloja en `data/models/` y en el HDD del Equipo 2.
2. **Amplificador de Variedad de Gestión (Agente Supervisor en `n8n` + LLM Gateway con Failover):** Transforma las predicciones y los valores SHAP en informes ejecutivos y recomendaciones diferenciadas por provincia y sector (**Salud/DIRESA**, **Agua y Saneamiento/DRVCS**, **Agricultura/MIDIS/MEF**) alineadas a los Objetivos Estratégicos Institucionales (**OEI**) del **PEI 2020–2027 Ampliado** del GORE Huancavelica. La orquestación en `n8n` (`AI Agent v3.1`) opera con herramientas `@n8n/n8n-nodes-langchain.toolCode` conectadas al microservicio FastAPI (`:8000`), priorizando **Ollama (`llama3.2` con backend Vulkan en GTX 1050)** para la invocación local de herramientas y **Gemini (`gemini-flash-lite-latest`, nivel gratuito de Google AI Studio)** para la síntesis narrativa rápida y conmutación automática por fallo (*failover* de 3 niveles hasta plantilla determinista MSV).

### 5.2. Las 6 Herramientas del Agente Supervisor y las 3 Reglas Fijas Cibernéticas

Siguiendo los criterios de gobernanza algorítmica para el sector público de la CEPAL (Clavijo, 2026), el Agente Supervisor dispone de **6 herramientas** (`extraer_fuentes`, `consultar_bd`, `predecir_riesgo`, `explicar_riesgo`, `redactar_informe` y `notificar`) con salidas compactadas para proteger su ventana de contexto y un nodo normalizador (`Normalizar Salida S4 para Reglas Fijas`), pero **tres decisiones críticas permanecen en Reglas Fijas deterministas** fuera del alcance del LLM:

- **Regla Fija 1 (Inferencia Numérica Determinista):** La proyección de DCI y la probabilidad de riesgo las calcula exclusivamente el motor `CatBoost` (`/predict`), impidiendo cualquier estimación numérica inventada por el LLM.
- **Regla Fija 2 (Canal Algedónico Automatizado $\text{S1/S4} \rightarrow \text{S5}$):** Un nodo condicional fijo (`IF`) evalúa si la DCI proyectada supera el umbral crítico del **$25,0\,\%$**. Cuando se supera, la señal algedónica se despacha directamente al **Sistema 5 (Consejo Regional)** mediante Telegram Bot API real (`sendMessage` con reintentos) sin posibilidad de omisión ni demora por parte del agente.
- **Regla Fija 3 (Aprobación Humana en el Canal de Control $\text{S4} \rightarrow \text{S3}$):** Toda recomendación dirigida al **Sistema 3 (Gerencia Regional de Desarrollo Social)** nace en estado `PENDIENTE_APROBACION` (`publicado_en_canal_control_s3 = False`) y requiere aprobación humana explícita mediante nodo `sendAndWait` en Telegram (compuerta `¿Aprobado por Humano S3?`) antes de confirmarse vía `POST /hitl/aprobar/{alert_id}` hacia `APROBADO_S3`.

### 5.3. Sustento Teórico, Operativo y Estadístico del Sistema de Indicadores Vigentes

Antes de evaluar en la siguiente etapa el marco de indicadores sistémicos de Parra Luna, se consolidan y sustentan los **indicadores observacionales y territoriales actualmente integrados** en [`data/exports/panel_distrital_hvc_2014_2024.csv`](../data/exports/panel_distrital_hvc_2014_2024.csv) ($N = 1\,100$ registros, $100$ distritos entre `2014` y `2024`).

**Tabla 1**  
*Sustento Empírico y Descriptivo de los Indicadores Territoriales de Entrada por Dimensión MSV ($N = 1\,100$, Serie `2014–2024` y Corte `2024`)*

| Dimensión MSV / Fuente Oficial | Indicador Operativo (Unidad) | Media $\pm$ DE (`2014–2024`) | Rango (`Mín–Máx`) | Correlación $r$ con DCI | Corte `2024` $\text{S5}$ ($n=5$) vs $\text{S3}$ ($n=95$) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **1. Nutricional (`SIEN-HIS`)** | `tasa_dci_pct` (%) | $22,63 \pm 5,50$ | $8,50 - 40,35$ | $+1,000$ | **$25,65\,\%$ vs $16,87\,\%$** ($+8,78\text{ pp}$) |
| **1. Nutricional (`SIEN-HIS`)** | `tasa_anemia_pct` (%) | $53,84 \pm 10,82$ | $28,00 - 76,00$ | $+0,994$ | **$57,45\,\%$ vs $41,33\,\%$** ($+16,12\text{ pp}$) |
| **1. Nutricional (`SIEN-HIS`)** | `tasa_bajo_peso_pct` (%) | $5,89 \pm 1,43$ | $2,21 - 10,49$ | $+1,000$ | **$6,67\,\%$ vs $4,39\,\%$** ($+2,28\text{ pp}$) |
| **2. Socioeconómica (`INEI`)** | `pobreza_monetaria_pct` (%) | $41,51 \pm 8,93$ | $18,00 - 67,69$ | $+0,959$ | **$46,26\,\%$ vs $32,90\,\%$** ($+13,36\text{ pp}$) |
| **2. Socioeconómica (`ENDES`)** | `educacion_materna_secundaria_pct` (%) | $59,24 \pm 5,85$ | $48,16 - 82,70$ | $-0,814$ | **$64,38\,\%$ vs $66,87\,\%$** ($-2,48\text{ pp}$) |
| **2. Territorial (`INEI`)** | `ruralidad_pct` (%) | $79,50 \pm 12,23$ | $22,50 - 92,30$ | $+0,543$ | **$87,92\,\%$ vs $79,05\,\%$** ($+8,87\text{ pp}$) |
| **3. Agua segura (`ENDES`)** | `agua_cloro_adecuado_pct` (%) | $8,17 \pm 3,98$ | $3,50 - 25,96$ | $-0,889$ | **$7,76\,\%$ vs $12,28\,\%$** ($-4,52\text{ pp}$) |
| **3. Saneamiento (`ENDES`)** | `saneamiento_basico_pct` (%) | $56,33 \pm 6,52$ | $44,00 - 80,15$ | $-0,799$ | **$63,14\,\%$ vs $65,45\,\%$** ($-2,31\text{ pp}$) |
| **3. Salud (`ENDES`)** | `controles_cred_completo_pct` (%) | $62,37 \pm 6,25$ | $51,08 - 79,85$ | $-0,737$ | **$70,69\,\%$ vs $71,93\,\%$** ($-1,24\text{ pp}$) |
| **3. Prácticas (`ENDES`)** | `lactancia_materna_exclusiva_pct` (%) | $83,54 \pm 1,94$ | $74,70 - 87,08$ | $+0,012$ | $86,55\,\%$ vs $85,49\,\%$ ($+1,07\text{ pp}$) |
| **4. Presupuesto (`MEF PAN`)** | `ejecucion_pan_mef_pct` (%) | $71,10 \pm 6,41$ | $56,32 - 89,40$ | $-0,713$ | $79,07\,\%$ vs $78,17\,\%$ ($+0,90\text{ pp}$) |
| **4. Presupuesto (`MEF PAN`)** | `presupuesto_pan_per_capita_soles` (S/) | $464,90 \pm 67,73$ | $320,00 - 608,00$ | $-0,476$ | S/ $564,80$ vs S/ $554,38$ ($+10,42$) |
| **4. Protección (`MIDIS`)** | `cobertura_juntos_pct` (%) | $80,44 \pm 4,35$ | $59,20 - 87,54$ | $+0,222$ | $86,14\,\%$ vs $83,30\,\%$ ($+2,84\text{ pp}$) |
| **4. Protección (`MIDIS`)** | `cobertura_cuna_mas_pct` (%) | $56,90 \pm 5,06$ | $38,50 - 66,46$ | $-0,272$ | $65,58\,\%$ vs $63,81\,\%$ ($+1,77\text{ pp}$) |
| **4. Escolar (`MIDIS`)** | `cobertura_qali_warma_pct` (%) | $89,00 \pm 3,16$ | $84,00 - 94,00$ | $-0,611$ | $94,00\,\%$ vs $94,00\,\%$ ($0,00\text{ pp}$) |
| **5. Climática (`SENAMHI`)** | `dias_heladas_anual` (días/año) | $69,17 \pm 26,66$ | $23,00 - 160,00$ | $+0,560$ | **$121,60$ vs $66,15$** ($+55,45\text{ d}$) |
| **5. Climática (`SENAMHI`)** | `temp_minima_promedio_c` (°C) | $2,02 \pm 1,87$ | $-4,31 - 5,20$ | $-0,559$ | **$-1,81\,^\circ\text{C}$ vs $+2,23\,^\circ\text{C}$** ($-4,04\,^\circ\text{C}$) |
| **5. Climática (`SENAMHI`)** | `precipitacion_anual_mm` (mm) | $800,42 \pm 58,92$ | $599,10 - 915,00$ | $-0,340$ | $669,48$ vs $806,39$ ($-136,91\text{ mm}$) |
| **5. Geográfica (`INEI`)** | `altitud_msnm` (m s. n. m.) | $3\,273,39 \pm 439,24$ | $1\,916 - 4\,473$ | $+0,504$ | **$4\,152,6$ vs $3\,227,1$** ($+925,5\text{ m}$) |

*Nota.* Estadísticos calculados directamente sobre el panel histórico consolidado (`panel_distrital_hvc_2014_2024.csv`). Entre `2014` y `2024`, la media distrital de DCI descendió de $27,92\,\%$ a $17,31\,\%$ ($-10,61\text{ pp}$), la anemia de $65,32\,\%$ a $42,13\,\%$ ($-23,19\text{ pp}$), el acceso a agua con cloro adecuado subió de $4,74\,\%$ a $12,05\,\%$ ($+7,31\text{ pp}$) y la ejecución del PAN `0001` pasó de $63,98\,\%$ a $78,21\,\%$ ($+14,23\text{ pp}$).

El análisis de la **Tabla 1** sustenta tres hallazgos cibernéticos fundamentales para el diseño del Sistema 4:

1. **Multicolinealidad estructural de la trampa nutricional (S1–Ambiente):** La DCI se asocia fuertemente con la anemia infantil ($r = +0,994$) y la pobreza monetaria ($r = +0,959$), mientras que las covariables protectoras de mayor correlación negativa son el agua rural con cloro adecuado ($r = -0,889$), la educación secundaria materna ($r = -0,814$), el saneamiento básico ($r = -0,799$), los controles CRED completos ($r = -0,737$) y la ejecución presupuestal del PAN `0001` ($r = -0,713$).
2. **Brecha crítica entre distritos $\text{S5}$ y $\text{S3}$:** En el corte `2024`, los distritos que activan el Canal Algedónico $\text{S5}$ casi duplican los días de heladas anuales frente al resto de la región ($121,60$ frente a $66,15$ días/año), se ubican en promedio $925,5\text{ m}$ más alto ($4\,152,6\text{ m s. n. m.}$) y conservan una cobertura de agua adecuadamente clorada crítica ($7,76\,\%$ frente a $12,28\,\%$).
3. **Lectura institucional del sesgo de focalización (MIDIS / MEF):** En el corte transversal, la cobertura de `Juntos` ($r = +0,222$; $86,14\,\%$ en $\text{S5}$ vs $83,30\,\%$ en $\text{S3}$) y la ejecución porcentual del PAN en `2024` ($79,07\,\%$ vs $78,17\,\%$) aparecen tan altas o mayores en los distritos críticos porque los programas sociales focalizan precisamente las zonas de mayor pobreza extrema. Esto demuestra que **la cobertura nominal o el gasto ejecutado por sí solos son insuficientes como indicadores de control**: el Sistema 3 necesita monitorear conjuntamente la calidad física del entorno (cloro residual $\ge 0,5\text{ mg/L}$, OEI.04) y la mitigación térmica (OEI.10), lo cual justifica incorporar en la próxima semana los indicadores de eficacia y realización de Parra Luna.

---

## Capítulo 6. Evaluación del Desempeño Predictivo, Explicabilidad XAI ($\text{S3}^*$) e Indicadores Operativos

### 6.1. Validación Cruzada Estratificada del Motor Predictivo (`2014–2024`)

La validación del motor predictivo sobre el panel histórico integrado de los **100 distritos de Huancavelica (`2014–2024`, $N = 1\,100$)** superó la meta académica de referencia ($\text{AUC-ROC} \ge 0,90$) establecida por Navarro-Guillén et al. (2026) para vigilancia nutricional sobre registros del SIEN en el Perú.

**Tabla 2**  
*Métricas Globales de Desempeño del Motor Predictivo CatBoost + SHAP (Validación 2014–2024, $N = 1\,100$)*

| Métrica de Evaluación | Valor Obtenido | Meta de Referencia (Navarro-Guillén et al., 2026) | Estado y Sustento Cibernético |
| :--- | :---: | :---: | :--- |
| **Área Bajo la Curva ROC ($\text{AUC-ROC}$)** | **$0,9993$** | $\ge 0,9000$ | **Cumple ($+0,0993$):** Separación casi perfecta de distritos en riesgo |
| **Puntaje $\text{F1-Score}$** | **$0,8917$** | $\ge 0,8500$ | **Cumple:** Equilibrio sólido precisión–sensibilidad (`0,8881` en corte PG live) |
| **Sensibilidad (*Recall* en distritos críticos)** | **$1,0000$** | $\ge 0,9000$ | **Cumple ($\text{FN} = 0$):** Cero distritos críticos omitidos por S4 |
| **Precisión (*Precision*)** | **$0,8046$** | $\ge 0,8000$ | **Cumple:** Tasa controlada de falsas alarmas ($\text{FP} = 93$) auditable en $\text{S3}^*$ |
| **Exactitud Global (*Accuracy*)** | **$91,55\,\%$** | $\ge 85,00\,\%$ | **Cumple:** Consistente entre evaluación local y servidor PostgreSQL |

*Nota.* Matriz de confusión sobre $N = 1\,100$: Verdaderos Positivos ($\text{TP} = 383$), Verdaderos Negativos ($\text{TN} = 624$), Falsos Positivos ($\text{FP} = 93$), Falsos Negativos ($\text{FN} = 0$). Desde la perspectiva del MSV, la asimetría entre $\text{FN} = 0$ y $\text{FP} = 93$ es intencional y deseable: el costo social de omitir un distrito en crisis nutricional supera ampliamente el costo administrativo de someter un caso limítrofe a revisión de Auditoría ($\text{S3}^*$). La curva ROC y la matriz de confusión de entrenamiento se documentan en [`docs/figures/fig1_roc_cv5_catboost_hvc.png`](figures/fig1_roc_cv5_catboost_hvc.png) y [`docs/figures/colab_roc_confusion_sentinelnutri.png`](figures/colab_roc_confusion_sentinelnutri.png).

### 6.2. Homeostato $\text{S3–S4}$ por Provincia y Red de Salud ($\text{S2}$)

**Tabla 3**  
*Desempeño y Estado del Homeostato S3–S4 por Provincia y Red de Salud (Coordinación S2, Corte 2024 Exportado)*

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

*Nota.* Visualización comparativa en [`docs/figures/fig4_homeostato_s3_s4_7_provincias.png`](figures/fig4_homeostato_s3_s4_7_provincias.png).

### 6.3. Auditoría de Explicabilidad XAI mediante Valores SHAP (Soporte a S3*)

Para impedir que el atenuador opere como una «caja negra», la herramienta `explicar_riesgo` descompone cada proyección distrital mediante valores de Shapley (`SHAP`), respaldando la auditoría de **$\text{S3}^*$**.

**Tabla 4**  
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

*Nota.* Los gráficos globales y locales se encuentran en [`docs/figures/fig2_shap_importancia_global_s3_star.png`](figures/fig2_shap_importancia_global_s3_star.png), [`docs/figures/fig3_shap_waterfall_distrito_critico.png`](figures/fig3_shap_waterfall_distrito_critico.png), [`docs/figures/colab_shap_beeswarm_global.png`](figures/colab_shap_beeswarm_global.png) y [`docs/figures/colab_shap_waterfall_distrital.png`](figures/colab_shap_waterfall_distrital.png). Obsérvese la convergencia entre la Tabla 1 y la Tabla 4: aunque la anemia posee alta colinealidad lineal con la DCI ($r = +0,994$), `CatBoost + SHAP` asigna el segundo y tercer mayor peso causal directo al **agua clorada (`1,1306` pp)** y a las **heladas (`1,0904` pp)**, identificando palancas accionables para DRVCS (OEI.04) y SENAMHI/Agricultura (OEI.10).

### 6.4. Indicadores Operativos y de Gobernanza Cibernética Verificados hasta la Fecha

Además de los indicadores territoriales y predictivos, el despliegue dual en el Equipo 2 y la batería automatizada de pruebas permiten sustentar **seis indicadores operativos** medidos en ejecución real:

**Tabla 5**  
*Indicadores Operativos de Operación Cibernética, Cumplimiento Normativo y Verificación (Estado Actual)*

| Indicador Operativo | Valor Medido / Observado | Evidencia y Alcance de Verificación |
| :--- | :---: | :--- |
| **Cobertura de catálogo territorial MSV** | **$100 / 100$ distritos** ($1\,100$ filas `2014–2024`) | Tablas `cat_ubigeo_hvc` y `serie_historica_distrital` (SQLite y PostgreSQL 16) |
| **Tasa de disparo del Canal Algedónico $\text{S5}$** | **$5,0\,\%$** ($5/100$ exportado) · **$4,0\,\%$** ($4/100$ vivo PG) | Regla Fija 2 determinista ($> 25,0\,\%$) en `/predict` y n8n |
| **Efectividad del Guardarraíl Ley N.º 29733** | **$100\,\%$ de rechazo nominal** (`HTTP 422`) | Bloqueo comprobado en vivo ante `dni`/`DNI_Menor` y ajuste `"direccion" -> "efecto"` (`cbda0d1`) |
| **Integridad de vigilancia `SHA-256` (Tool 1)** | **$6 / 6$ portales** auditados por huella | SIEN-HIS, ENDES, INEI Pobreza, MEF PAN, MIDIS y SENAMHI en `registro_cargas` |
| **Disponibilidad del Gateway LLM (Tool 5)** | **3 niveles operativos** (`gemini-flash-lite-latest` activo) | Verificado en vivo en ensayo LAN: respuesta real Gemini y failover automático Ollama $\rightarrow$ Gemini |
| **Confiabilidad automatizada (`Red-Team QA`)** | **$22 / 22$ pruebas aprobadas (`100\,\%`)** | Suite `tests/run_all_tests.py` ejecutada tras la sincronización de commits (`165e0ee`) |

---

## Capítulo 7. Gobernanza Cibernética, Privacidad, Evidencia en Vivo y Próxima Fase

### 7.1. Distritos Críticos que Disparan el Canal Algedónico Automatizado ($\text{S1/S4} \rightarrow \text{S5}$)

En el corte exportado (`matriz_gobernanza_oei_ods_hvc.csv`), la **Regla Fija 2** (`DCI proyectada > 25,0 %`) identificó **5 registros distritales en alerta algedónica crítica** (`S5_ALGEDONICO`) y ubicó a **Nuevo Occoro (`090114`, $24,96\,\%$)** exactamente en la frontera de control $\text{S3}$ (`S3_CONTROL`), caso utilizado para validar en vivo la compuerta humana HITL (`Regla Fija 3`).

**Tabla 6**  
*Registros Críticos del Corte Exportado que Activan el Canal Algedónico ($\text{S5}$) y Caso Frontera de Control ($\text{S3}$)*

| Ubigeo | Provincia | Distrito | DCI Actual S3 (%) | DCI Proyectada S4 (%) | Canal MSV Activado | Determinante Principal SHAP ($\text{S3}^*$) |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- |
| `090411` | Castrovirreyna | **Santa Ana** | $28,14\,\%$ | **$29,29\,\%$** | `S5_ALGEDONICO` | Inercia DCI + Heladas altoandinas (`OEI.10`) |
| `090607` | Huaytará | **Pilpichaca** (registro 1) | $25,75\,\%$ | **$26,42\,\%$** | `S5_ALGEDONICO` | Heladas extremas + Baja cloración (`OEI.04/OEI.10`) |
| `090606` | Huaytará | **Pilpichaca** (registro 2) | $25,39\,\%$ | **$25,93\,\%$** | `S5_ALGEDONICO` | Heladas altoandinas + Brecha de agua segura |
| `090106` | Huancavelica | **Huachocolpa** | $24,75\,\%$ | **$25,65\,\%$** | `S5_ALGEDONICO` | Días de heladas al año (`+1,71 pp` SHAP en vivo) |
| `090304` | Angaraes | **Ccochaccasa** | $24,21\,\%$ | **$25,04\,\%$** | `S5_ALGEDONICO` | Agua sin cloro adecuado + Heladas (`4 150 msnm`) |
| `090114` | Huancavelica | **Nuevo Occoro** *(frontera)* | $24,09\,\%$ | **$24,96\,\%$** | `S3_CONTROL` | Días de heladas al año (`+1,53 pp` SHAP en vivo) |

*Nota.* En la base de datos viva PostgreSQL del Equipo 2 durante el ensayo E2E, `Ccochaccasa` (`25,04 %` en exportación local) queda justo por debajo del umbral, arrojando `4` alertas S5 con `Huachocolpa (090106, 25,65 %)` como caso crítico principal para el despacho inmediato `S5_ALGEDONICO` y `Nuevo Occoro (090114, 24,96 %)` como caso testigo para la aprobación humana `HITL -> APROBADO_S3`.

### 7.2. Verificación Técnica de Ética y Privacidad de Datos (Ley N.º 29733)

1. **Cumplimiento de la Ley N.º 29733 (Protección de Datos Personales):** El módulo [`privacy_guard.py`](../src/sentinelnutri/domain/rules/privacy_guard.py) inspecciona recursivamente todo diccionario antes de invocar la herramienta `redactar_informe` hacia la API de Gemini u Ollama. Si detecta cualquier campo nominal (`dni`, `nombres`, `apellidos`, `historia_clinica`, `direccion`, `fecha_nacimiento_exacta`), bloquea la solicitud lanzando `PrivacyViolationError` (`HTTP 422`), garantizando que hacia los proveedores de LLM solo viajen indicadores agregados por distrito. Adicionalmente, en el commit `cbda0d1` se reemplazó la clave `"direccion"` de impacto SHAP por `"efecto"` en [`tool_3_predecir_riesgo.py`](../src/sentinelnutri/application/tool_3_predecir_riesgo.py) para evitar falsos positivos al encadenar `Tool 3 -> Tool 5`.
2. **Extracción Responsable y Trazabilidad `SHA-256`:** El módulo [`scraping_ethics.py`](../src/sentinelnutri/domain/rules/scraping_ethics.py) valida el archivo `robots.txt` de cada portal estatal, identifica las peticiones con el encabezado académico `SentinelNutri-HVC/1.0 (Proyecto Academico FIIS-UNI; MSV-S4)` y registra en la tabla `registro_cargas` la huella digital `SHA-256` de cada archivo descargado.

### 7.3. Articulación con el PEI 2020–2027 del GORE Huancavelica y los ODS 2, 3 y 6

La matriz completa de los 100 distritos exportada en [`data/exports/matriz_gobernanza_oei_ods_hvc.csv`](../data/exports/matriz_gobernanza_oei_ods_hvc.csv) vincula cada alerta y recomendación sectorial del **Sistema 4** con los instrumentos estratégicos regionales y globales:

- **ODS 2 (Hambre Cero — Meta 2.2) $\leftrightarrow$ OEI.01 y OEI.08 del PEI 2020–2027:** Reducción de la desnutrición crónica y anemia en menores de 5 años mediante focalización temprana de controles CRED, suplementación de hierro y protección agropecuaria altoandina.
- **ODS 3 (Salud y Bienestar — Meta 3.2) $\leftrightarrow$ OEI.01 y OEI.03 del PEI 2020–2027:** Coordinación interprovincial (**S2**) de las 7 Redes de Salud de la DIRESA Huancavelica y mejora de la calidad de ejecución del Programa Articulado Nutricional (`0001`).
- **ODS 6 (Agua Limpia y Saneamiento — Meta 6.1) $\leftrightarrow$ OEI.04 del PEI 2020–2027:** Intervención prioritaria sobre sistemas de cloración rural (`agua_cloro_adecuado_pct` como segundo predictor global con $|\text{SHAP}| = 1,1306\text{ pp}$).

### 7.4. Evidencia Operativa en Vivo y Ensayo End-to-End (Equipo 1 $\leftrightarrow$ Equipo 2 LAN)

Las capturas en vivo tomadas directamente sobre los servicios encapsulados en Docker en el **Equipo 2 (`DESKTOP-H3C8P9R`, PostgreSQL 16 + FastAPI `:8000` + n8n `:5678` + Streamlit `:8501` + Ollama Vulkan GTX 1050 `:11434`)** se documentan en [`docs/figures/`](figures/):

1. **Sala 1 — Homeostato $\text{S3–S4}$ (`:8501`):** [`equipo2_live_01_dashboard_homeostato_s4_s3.png`](figures/equipo2_live_01_dashboard_homeostato_s4_s3.png)
2. **Sala 2 — Auditoría $\text{S3}^*$ mediante Explicabilidad SHAP:** [`equipo2_live_02_dashboard_s3_star_auditoria_shap.png`](figures/equipo2_live_02_dashboard_s3_star_auditoria_shap.png)
3. **Sala 3 — Coordinación Interprovincial $\text{S2}$ de las 7 Redes de Salud:** [`equipo2_live_03_dashboard_s2_coordinacion_redes.png`](figures/equipo2_live_03_dashboard_s2_coordinacion_redes.png)
4. **Sala 4 — Canal Algedónico $\text{S5}$, Aprobación Humana HITL y `SHA-256`:** [`equipo2_live_04_dashboard_s5_canal_algedonico_ods.png`](figures/equipo2_live_04_dashboard_s5_canal_algedonico_ods.png)
5. **Microservicio REST FastAPI con las 6 Herramientas (`:8000/docs`):** [`equipo2_live_05_fastapi_swagger_6_tools.png`](figures/equipo2_live_05_fastapi_swagger_6_tools.png)
6. **Orquestador Agéntico `n8n` en SSD (`:5678`):** [`equipo2_live_06_n8n_orchestrator.png`](figures/equipo2_live_06_n8n_orchestrator.png) y [`equipo2_live_07_n8n_trial_run.png`](figures/equipo2_live_07_n8n_trial_run.png)

Adicionalmente, el **ensayo de demostración End-to-End en vivo sobre red local** ejecutado desde el Equipo 1 contra el Equipo 2 (`python scripts/ensayo_flujo_e2e.py --host 192.168.1.6`) completó las **7 etapas en $53,94\text{ s}$**: validación de los 4 servicios de infraestructura, ingesta `weekly_watch` de 6 portales (`Tool 1`), consulta de $1\,100$ registros (`Tool 2`), inferencia `CatBoost` en $10,89\text{ s}$ (`Tool 3`), explicación SHAP para `Huachocolpa` y `Nuevo Occoro` (`Tool 4`), bloqueo de datos nominales `HTTP 422` y redacción en vivo con **`gemini-flash-lite-latest`** incluyendo conmutación automática por failover cuando `Ollama` excedió el umbral (`Tool 5`), despacho directo `S5_ALGEDONICO` (`Alerta ID=26`) y compuerta humana HITL completa `PENDIENTE_APROBACION -> APROBADO_S3` (`Alerta ID=27`).

### 7.5. Proyección de la Siguiente Iteración: Evaluación de Indicadores de Parra Luna (Próxima Semana)

Con el panel histórico consolidado (`1 100` registros), el motor XAI validado ($\text{AUC-ROC} = 0,9993$) y la infraestructura operativa verificada end-to-end, la **próxima semana** se evaluará la pertinencia y formulación formal de los **indicadores sistémicos de Francisco Parra Luna** aplicados al caso SentinelNutri-HVC:

- Se analizará cómo mapear las variables reales ya recolectadas en PostgreSQL (por ejemplo, `dci_actual_pct`, `dci_proyectada_pct`, `ejecucion_pan_mef_pct`, `agua_cloro_adecuado_pct`, coberturas MIDIS y latencias de respuesta $\text{S3–S4–S5}$) dentro de la taxonomía de Parra Luna (*actualidad*, *capacidad/potencialidad*, *eficacia*, *eficiencia* y *efectividad* institucional frente a los OEI del PEI 2020–2027).
- Los resultados de dicha evaluación se incorporarán como módulo analítico adicional en el Dashboard y como sección complementaria del informe final una vez validados con los criterios de la cátedra.
