# Diccionario de datos del legajo fiscal digital

**Versión:** 1.0 · **Fecha:** 2026-07-06
**Alcance:** describe campo por campo el JSON del legajo (`salidas/legajos/legajo_*.json`), su tipo, la fuente de la que proviene cada dato y su significado operativo. Es el anexo formal para auditoría interna, externa o inspección: permite interpretar la evidencia sin acceso al código.

> Un legajo se **sella al crearse** (estado `cerrado` + hash SHA256). Cualquier modificación posterior del archivo es detectable: al consultar el legajo, el sistema recalcula el hash y lo compara con el registrado.

## 1. Campos raíz

| Campo | Tipo | Fuente | Significado |
|---|---|---|---|
| `id` | string | sistema | Identificador único: `legajo_AAAAMMDD_HHMMSS_<8 hex>`. |
| `creado_en` | string fecha-hora | sistema | Momento de creación y sellado (`AAAA-MM-DD HH:MM:SS`, hora del servidor). |
| `estado` | string | sistema | `cerrado`: el legajo se sella al crearse y no se modifica. Legajos previos al sellado figuran `sin_sellar` en el listado. |
| `sha256` | string (64 hex) | sistema | Hash SHA256 del legajo canónico (JSON ordenado por clave, excluyendo este campo). Base de la verificación de integridad. |
| `excel` | string | sistema | Nombre del reporte Excel asociado en `salidas/`. |
| `total_proveedores` | int | sistema | Cantidad de CUITs evaluados en la corrida. |
| `reglas_aplicadas` | objeto | catálogos | Versiones de los catálogos de reglas vigentes al decidir (ver §2). |
| `padrones_snapshot` | objeto | manifest de padrones | Metadata de los padrones usados (ver §3). |
| `resumen` | lista | derivado | Una línea por proveedor con la decisión (ver §4). |
| `resultados` | lista | consulta | Evidencia completa por proveedor (ver §5). |
| `integridad` | objeto | calculado al consultar | Solo en la respuesta de la API (no persiste): `valido` (bool), `sha256_registrado`, `sha256_recalculado`. |

## 2. `reglas_aplicadas`

Reconstruibilidad: qué versión de las reglas se usó en esta decisión.

| Campo | Tipo | Fuente | Significado |
|---|---|---|---|
| `regimenes_catalogo.version` | int | `config/regimenes_catalogo.json` | Versión del catálogo de regímenes fiscales aplicada. |
| `regimenes_catalogo.actualizado` | string fecha | ídem | Fecha de última actualización de ese catálogo. |
| `clientes_agentes.version` | int | `config/clientes_agentes.json` | Versión del catálogo de clientes-agentes (huella del cliente). |
| `clientes_agentes.actualizado` | string fecha | ídem | Fecha de última actualización. |

## 3. `padrones_snapshot`

Por cada provincia consultada con padrón registrado en el manifest:

| Campo | Tipo | Fuente | Significado |
|---|---|---|---|
| `periodo` | string | manifest | Período del padrón cargado (p. ej. `2026-06`). |
| `sha256` | string | manifest | Hash del archivo de padrón original importado. |
| `vigencia_hasta` | string fecha | manifest | Fin de vigencia declarado al importar. |
| `cargado_en` | string fecha-hora | manifest | Cuándo se importó el padrón. |

## 4. `resumen[]` (una entrada por proveedor)

| Campo | Tipo | Fuente | Significado |
|---|---|---|---|
| `cuit` / `cuit_limpio` | string | entrada + validador | CUIT formateado (`XX-XXXXXXXX-X`) y solo dígitos. |
| `razon_social` | string | ARCA | Denominación informada por la constancia (o `—`). |
| `estado_afip` | string | ARCA | Estado de la clave fiscal (`ACTIVO`, etc.). |
| `modo_afip` | string | sistema | `live` (consulta real), `demo` (fallback sin evidencia productiva) o `skip` (CUIT inválido). |
| `decision` / `decision_estado` | string | motor de decisión | Etiqueta y código: `APROBABLE`, `OBSERVADO`, `REVISION_MANUAL`, `BLOQUEAR`. |

## 5. `resultados[]` — evidencia completa por proveedor

### 5.1 Identificación y validación matemática

| Campo | Tipo | Fuente | Significado |
|---|---|---|---|
| `cuit`, `cuit_limpio` | string | validador | Como en §4. |
| `valido` | bool | validador (algoritmo DV ARCA) | Dígito verificador correcto. Un cálculo de DV=10 se rechaza (CUIT inexistente). |
| `tipo_persona` | string | prefijo CUIT | Persona Humana (20/23-27) / Persona Jurídica (30/33/34) / Otro. |
| `mensaje_validador` | string | validador | Detalle del resultado matemático. |
| `timestamp` | string | sistema | Momento de la consulta. |
| `modo_afip` | string | sistema | Ver §4. En `demo` la decisión nunca puede ser APROBABLE. |

### 5.2 `afip` — constancia ARCA

| Campo | Tipo | Fuente | Significado |
|---|---|---|---|
| `modo` | string | sistema | `live` o `demo`. |
| `encontrado` | bool | ARCA | Si el WS devolvió datos de persona. |
| `razon_social`, `tipo_persona`, `estado_clave` | string | ARCA (getPersona) | Datos generales de la constancia. |
| `condicion_iva` | string | ARCA | Impuesto IVA y estado (`IVA (ACTIVO)`, `MONOTRIBUTO — Categoría X`, etc.). |
| `condicion_ganancias` | string | ARCA | Ídem para Ganancias. |
| `inscripciones_iibb.regimen` | string | ARCA | `Convenio Multilateral`, `Ingresos Brutos` o `—`. |
| `inscripciones_iibb.jurisdicciones` | lista | ARCA (heurística) | Jurisdicciones detectadas en la constancia. **Advertencia:** incluye detección textual (puede tomar la provincia del domicilio); no reemplaza padrones provinciales. |
| `inscripciones_iibb.impuestos` | lista | ARCA | Impuestos IIBB/CM normalizados con estado. |
| `domicilio_fiscal`, `actividad_principal`, `fecha_inicio` | string | ARCA | Datos de la constancia. |
| `en_apoc` | bool o null | ARCA | `true`: figura en base APOC (bloqueo). `false`: verificado negativo. **`null`: NO VERIFICADO** — la consulta APOC no está integrada; el motor deriva a revisión manual. Nunca se informa "no figura" sin consulta real. |

### 5.3 `padrones` — cruce con padrones provinciales (por provincia)

| Campo | Tipo | Fuente | Significado |
|---|---|---|---|
| `status` | string | padrón local/Supabase | `inscripto`, `no_inscripto`, `no_disponible`, `consulta_manual`, `requiere_credenciales`. |
| `detalle` | string | sistema | Incluye el estado de vigencia del padrón y las alícuotas si está inscripto. **`no_inscripto` no implica "no retener"**: el tratamiento del no incluido depende del régimen local (puede ser alícuota general/residual/máxima). |
| `vigencia_estado` | string | manifest | `vigente`, `por_vencer`, `vencido`, `sin_vigencia`. Un padrón vencido degrada la decisión a OBSERVADO. |
| `vigencia_hasta_padron` | string | manifest | Fin de vigencia del padrón usado. |
| `alicuota_retencion` / `alicuota_percepcion` | string | padrón | Alícuotas del renglón del proveedor (si inscripto), normalizadas con punto decimal. |
| `vigencia_desde` / `vigencia_hasta` | string | padrón | Vigencia del renglón según el archivo. |
| `regimen` | string | padrón | Régimen/categoría informada por la jurisdicción. |
| `fuente` | string | sistema | `supabase` cuando el dato salió del índice remoto. |

### 5.4 `fuentes_online` — jurisdicciones sin padrón mensual

| Campo | Tipo | Fuente | Significado |
|---|---|---|---|
| `estado` | string | consulta online | `encontrado`, `no_encontrado`, `requiere_captcha`, `requiere_credenciales`, `requiere_navegador`, `error`, `revisar`. Los estados asistidos generan tarea en la cola (`/fuentes-pendientes`) y derivan a revisión manual: una fuente no consultable **nunca** se interpreta como "no inscripto". |
| `detalle`, `url_consulta`, `timestamp` | string | consulta online | Evidencia de la consulta. |

### 5.5 `decision_fiscal` — motor de decisión

| Campo | Tipo | Fuente | Significado |
|---|---|---|---|
| `estado` / `label` | string | motor | `APROBABLE` (0), `OBSERVADO` (1), `REVISION_MANUAL` (2), `BLOQUEAR` (3). Se toma siempre el máximo de severidad. |
| `score` | int | motor | Código de severidad (0-3). |
| `motivos` | lista | motor | Razones textuales de la decisión (CUIT inválido, modo demo, APOC no verificado, estado no activo, monotributo, padrones inscriptos/faltantes/vencidos, fuentes pendientes). |
| `recomendaciones` | lista | motor | Próxima acción sugerida por motivo. |

### 5.6 `matriz_tributaria` — consolidación de señales

| Campo | Tipo | Fuente | Significado |
|---|---|---|---|
| `items[]` | lista | consolidado | Por jurisdicción/impuesto: `condicion`, `retencion`, `percepcion` (alícuotas informadas por padrón o "según régimen"), `fuente`, `accion`. **No liquida**: consolida para que Impuestos decida. |
| `alertas[]` | lista | consolidado | Faltantes de padrón, fuentes manuales, monotributo, padrón vencido, y proveedor no incluido en padrón de jurisdicción con presencia detectada. |
| `resumen` | string | consolidado | Conteo de items y alertas. |

### 5.7 `regimenes_aplicables` — derivación por régimen

| Campo | Tipo | Fuente | Significado |
|---|---|---|---|
| `items[]` | lista | catálogo + señales | Por régimen del catálogo: `clasificacion` = `aplicable` (evidencia positiva), `potencial`, `pendiente_evidencia`, `no_integrable_cola_asistida`; con `motivos`, `evidencia_requerida`, `proxima_accion` e `integracion_fuente`. |
| `jurisdicciones_detectadas` | lista | ARCA + georef + padrones | Huella territorial detectada del proveedor. |
| `resumen` | objeto | derivado | Totales por clasificación y cuántos requieren acción. |

### 5.8 `georef`

| Campo | Tipo | Fuente | Significado |
|---|---|---|---|
| `provincia` | string o null | API georef datos.gob.ar | Provincia normalizada del domicilio fiscal ARCA. |
| `fuente` | string | sistema | Siempre `georef.datos.gob.ar`. |

## 6. Garantías y límites de la evidencia

1. **Integridad**: el hash SHA256 cubre todo el contenido; la verificación corre en cada consulta del legajo.
2. **Reconstruibilidad**: versiones de catálogos + snapshot de padrones permiten reproducir el contexto normativo de la decisión.
3. **Honestidad de datos**: lo no verificado se marca como tal (`en_apoc: null` → "NO VERIFICADO"; fuentes asistidas → revisión manual; padrón vencido → advertencia explícita). El sistema no afirma ausencias que no consultó.
4. **Límite**: el legajo es asistencia y evidencia; no reemplaza el criterio profesional de Impuestos ni la liquidación definitiva de retenciones/percepciones.
