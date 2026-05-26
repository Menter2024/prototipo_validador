# Plan de automatización de padrones y fuentes fiscales

## Objetivo

Mantener actualizado el universo de fuentes que una empresa mediana/grande necesita para operar como agente de retención, percepción e información en Argentina, con trazabilidad suficiente para auditoría interna y soporte ante reclamos.

## Sprint 1 implementado

- Catálogo versionado de fuentes en `config/fuentes_catalogo.json`.
- Evaluador operativo en `app/modules/fuentes_catalogo.py`.
- API `GET /api/fuentes`.
- Monitor web `/fuentes`.
- Script scheduler-friendly `scripts/revisar_fuentes.py`.

## Sprint 2 implementado

- Estrategia de descarga por fuente dentro del catálogo.
- Descarga controlada y evidencia en `app/modules/descarga_fuentes.py`.
- Manifest de descargas en `salidas/evidencias/fuentes/fuentes_descargas_manifest.json`.
- API `POST /api/fuentes/descargar`.
- Botones de relevamiento/descarga en `/fuentes`.
- CLI `scripts/descargar_fuentes.py`.

La implementación evita simular automatización donde el organismo exige credenciales. ARBA queda marcada como automatizable con CIT/Web Service del agente; AGIP queda como fuente pública con detección del enlace vigente; ATER queda como monitoreo de publicación/archivo oficial.

## Sprint 3 implementado

- Estrategia de descarga/circuito definida para las fuentes restantes del catálogo:
  - Córdoba, Jujuy y Tucumán: relevamiento de enlaces públicos.
  - Formosa: archivo/exportación cliente hasta confirmar padrón público normalizado.
  - Mendoza, Santa Fe y Corrientes: portal con credenciales.
  - Misiones: consulta pública por CUIT con navegador/asistencia.
  - Neuquén: consulta online por CUIT ya automatizada.
  - Río Negro: CAPTCHA asistido.
- ARCA/AFIP ahora normaliza señales de IIBB/Convenio Multilateral desde la constancia de inscripción.
- La matriz tributaria incorpora jurisdicciones IIBB informadas por ARCA como condición a cruzar contra padrones provinciales.
- Cola `/fuentes-pendientes` para gestionar intervenciones humanas con estado, nota, legajo asociado y evidencia adjunta.

### Criterio Convenio Multilateral

La inscripción en Ingresos Brutos bajo Convenio Multilateral y las jurisdicciones declaradas pueden surgir de la constancia de inscripción ARCA. Ese dato ayuda a definir **dónde debe analizarse el tratamiento provincial**.

Pero ARCA **no reemplaza** a los padrones o consultas provinciales: un contribuyente inscripto localmente solo en una provincia puede no figurar en ARCA como Convenio Multilateral. Por eso los padrones provinciales son necesarios para dos cosas:

- confirmar inscripción local en IIBB;
- determinar alícuotas, exclusiones, riesgo fiscal o tratamiento operativo como agente.

## Clasificación operativa

| Clase | Ejemplo | Automatización objetivo |
| --- | --- | --- |
| `api_oficial` | ARCA constancia | Consulta online por alta/revalidación |
| `padron_descargable` | ARBA, AGIP, ATER, Córdoba, Santa Fe | Descarga mensual + importador + manifiesto |
| `consulta_online` | Neuquén, Misiones | Consulta por CUIT con evidencia |
| `portal_captcha` | Río Negro | Cola asistida + captura |
| `portal_credenciales` | Corrientes | Credenciales cliente o exportación controlada |

## Cadencia mínima

- **ARCA inscripción:** en cada alta y revalidación.
- **Padrones mensuales provinciales:** revisión diaria de estado y carga mensual del período vigente.
- **Fuentes sin archivo mensual:** consulta por CUIT en altas nuevas y revalidación periódica por riesgo.
- **Fuentes con CAPTCHA o credenciales:** workflow asistido con responsable, evidencia y vencimiento.

## Próximos desarrollos

1. Automatizar descarga ARBA/AGIP/ATER donde exista archivo público estable.
   - Base Sprint 2: AGIP releva/descarga desde página pública; ARBA/ATER quedan parametrizadas según credencial/publicación.
2. Incorporar historial de ejecuciones de jobs y evidencias descargadas.
3. Implementar parsers específicos para archivos descargados en formato no estándar (`.rar`, `.xls`, layouts fijos).
4. Persistir resultados en base de datos multiempresa.
5. Agregar alertas por mail/Slack/Teams cuando una fuente crítica esté vencida o sin carga.
