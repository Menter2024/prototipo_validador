# Auditoría inicial de regímenes argentinos de retención, percepción e información

Fecha de corte: 2026-05-26.

## Objetivo

Construir una vista operativa completa para planificar la integración gradual de regímenes fiscales argentinos dentro de la plataforma. Este documento no reemplaza asesoramiento tributario ni normativa vigente; organiza familias, riesgos, fuentes e integración posible.

## Principio de arquitectura

Los regímenes no deben modelarse como portales aislados. Deben modelarse por:

- nivel: nacional, provincial, provincial unificado o municipal;
- tipo: retención, percepción, recaudación o información;
- familia fiscal;
- fuente de alícuota/padrón;
- sistema de presentación;
- evidencia requerida;
- grado realista de automatización.

El catálogo inicial vive en `config/regimenes_catalogo.json`.

## Clasificación general

| Nivel | Familia | Ejemplos | Integración objetivo |
| --- | --- | --- | --- |
| Nacional | Retenciones | Ganancias RG 830, IVA, SUSS, beneficiarios exterior | reglas + ARCA + certificados |
| Nacional | Percepciones | IVA, aduana, plataformas, moneda extranjera según vigencia | reglas + comprobantes + certificados |
| Nacional | Información | SIRE, Libro IVA Digital, IVA Simple, SITER | credenciales/exportación/acuses |
| Provincial unificado | COMARB | SIRCAR, SIRCREB, SIRTAC, SIRCUPA, SIRPEI, SIFERE, SIRCIP | portal/archivo/monitoreo |
| Provincial | IIBB local | ARBA, AGIP, Córdoba, Jujuy, Tucumán, Santa Fe, Mendoza | padrones + fuentes asistidas |
| Municipal | Tasas locales | TISH, DReI, Comercio e Industria, proveedores municipales | priorizar por huella cliente |

## Nacional ARCA

### Núcleo P0

- Ganancias RG 830 y regímenes vinculados a pagos.
- IVA retenciones y percepciones.
- SIRE/SICORE como sistemas de información/certificación.
- Libro IVA Digital / IVA Simple como fuente de conciliación mensual.

### Enfoque de integración

1. Normalizar condición fiscal del sujeto desde ARCA.
2. Resolver aplicabilidad del régimen según tipo de operación.
3. Asociar certificados de exclusión/no retención cuando existan.
4. Generar evidencia: constancia, parámetros usados, certificado y acuse.

Fuentes principales:

- https://www.arca.gob.ar/sire/
- https://www.arca.gob.ar/sire/ayuda/normativa.asp
- https://arca.gob.ar/gananciasYBienes/ganancias/retenciones/rg830/conceptos-alcanzados.asp
- https://www.afip.gob.ar/iva/iva-simple/
- https://biblioteca.arca.gob.ar/search/query/norma.aspx?p=t%3ARAG%7Cn%3A4597%7Co%3A3%7Ca%3A2019%7Cf%3A30%2F09%2F2019

## Provincial unificado / COMARB

Sistemas prioritarios:

| Sistema | Tipo | Uso operativo | Integración inicial |
| --- | --- | --- | --- |
| SIRCAR | retención/percepción | DDJJ agentes IIBB jurisdicciones adheridas | catálogo + cola credenciales |
| SIRCREB | recaudación | acreditaciones bancarias | padrón/evidencia asistida |
| SIRTAC | recaudación | tarjetas y medios de pago | padrón/evidencia asistida |
| SIRCUPA | recaudación | cuentas de pago/PSP | padrón/evidencia asistida |
| SIRPEI | percepción | importaciones | aduana/COMARB asistido |
| SIFERE | información/determinación | Convenio Multilateral | evidencia/acuses |
| SIRCIP | percepción | sistema unificado/emergente | monitoreo normativo |

Fuentes principales:

- https://www.argentina.gob.ar/economia/politicatributaria/armonizacion/comarb
- https://www.ca.gob.ar/sistemas/sircar
- https://www.ca.gob.ar/sistemas/sircupa
- https://www.ca.gob.ar/preguntas-frecuentes/sistemas/sirtac
- https://www.ca.gob.ar/preguntas-frecuentes/sistemas/sirpei/que-es-el-sirpei

## Provincial IIBB

### Estado recomendado

| Jurisdicción | Prioridad | Estrategia |
| --- | --- | --- |
| Buenos Aires / ARBA | P1 | credenciales/archivo + importador |
| CABA / AGIP | P1 | descarga pública + parser RAR/TXT |
| Entre Ríos / ATER | P1/P2 | monitoreo fuente estable |
| Córdoba | P2 | parser delimitado/ZIP + evidencia |
| Jujuy | P2 | parser XLSX + evidencia |
| Tucumán | P2 | parser CSV/TXT + evidencia |
| Santa Fe | P2 | portal credenciales/PARP |
| Mendoza | P2 | SIRCAR/ATM credenciales |
| Corrientes/Misiones/Neuquén/Río Negro | P3 | consulta/credenciales/CAPTCHA/asistido |

El producto ya tiene base para padrones provinciales y ahora debe conectar cada régimen del catálogo con el estado del padrón/fuente correspondiente.

## Municipal

No existe un equivalente unificado nacional. La estrategia correcta es priorizar por huella real del cliente:

1. domicilios fiscales y legales;
2. sucursales, depósitos y plantas;
3. municipios donde el cliente fue designado agente;
4. municipios donde concentra proveedores/ventas;
5. proveedores municipales si aplica.

El catálogo incluye un régimen marco `municipal_tish_drei_generico`. Luego se deben crear entradas específicas por municipio cuando haya cliente/operación concreta.

Ejemplos relevados:

- General Pueyrredón: https://www.concejomdp.gov.ar/biblioteca/docs/d2148-02.html
- Nogoyá: https://nuevo.nogoya.gob.ar/ordenanza-no891/
- Villa Gobernador Gálvez: https://concejovgg.gob.ar/ord-2533-18-regimen-de-retencion-de-derecho-de-registro-e-inspeccion-respecto-de-los-pagos-originados-en-facturas-que-se-efectuen-a-los-concesionarios-contratistas-y-proveedores-de-la-municipalida/

## Clases de automatización

| Clase | Significado | Tratamiento |
| --- | --- | --- |
| `automatizable` | API/archivo público estable | job + manifest + tests |
| `parcialmente_automatizable` | reglas + fuente digital, pero requiere credenciales o cálculo | motor + evidencia |
| `portal_credenciales_archivo` | portal privado/exportación | cola asistida + carga controlada |
| `descarga_publica_importador` | archivo público parseable | descarga + importador |
| `pagina_publica_importador_asistido` | publicación pública variable | monitor + confirmación |
| `priorizar_por_huella_cliente` | universo muy fragmentado | discovery por cliente |
| `monitoreo_normativo` | régimen emergente/cambiante | vigilancia + backlog |

## Roadmap recomendado

### Fase 1 — Catálogo maestro

- Mantener `config/regimenes_catalogo.json` con IDs estables.
- Validar integridad por tests.
- Cruzar cada fuente del catálogo de padrones con regímenes aplicables.

### Fase 2 — Motor de aplicabilidad

Resolver si una operación/proveedor cae en:

- IVA/Ganancias nacional;
- IIBB local o Convenio Multilateral;
- régimen provincial por padrón;
- régimen municipal por huella;
- exclusión/certificado.

### Fase 3 — Integraciones automáticas

Prioridad:

1. ARCA constancia y condición fiscal.
2. Padrones provinciales con archivo.
3. COMARB/SIRCAR/SIRCREB/SIRTAC/SIRCUPA/SIRPEI.
4. Santa Fe/Mendoza y portales credenciales.
5. Municipios priorizados por cliente.

### Fase 4 — Cola asistida

Para CAPTCHA, credenciales, ordenanzas PDF, portales no automatizables y fuentes municipales.

### Fase 5 — Seguimiento operativo

- vencimientos;
- padrones faltantes/vencidos;
- cambios de hash;
- variación contra períodos previos;
- evidencia y acuses.

## Próximo desarrollo sugerido

Crear módulo `app/modules/regimenes_catalogo.py` y endpoint `GET /api/regimenes` para visualizar el mapa, filtrar por nivel/prioridad/automatización y convertirlo en backlog operativo.

## Verificación normativa 2026-07-03 — SIRE/SICORE y calendarios 2026 (catálogo v2)

Cambios aplicados a `config/regimenes_catalogo.json` (versión 2):

- **SIRE y SICORE quedan modelados como sistemas separados que conviven**: `arca_sire` (RG AFIP 3726/2015 — IVA, Seguridad Social y Ganancias beneficiarios del exterior) y `arca_sicore` nuevo (RG AFIP 2233/2007 — regímenes no migrados, p. ej. Ganancias RG 830). Verificado con caso real: la constancia ARCA de CICSA (05/2026) muestra Ganancias por SICORE y los regímenes de IVA por SIRE desde 2020.
- **Calendario 2026 referenciado a norma, sin fechas hardcodeadas.** Criterio: las fechas puntuales se reprograman durante el año (ya ocurrió dos veces en 2026), por lo que el catálogo registra la norma del calendario, el esquema, la fuente oficial y el campo `norma_verificada_al`.
  - SIRCAR: RG CA 21/2025 (calendario 2026), modificada por **Disposición CA 1/2026** (BO 23/01/2026: presentación/pago desde el 5º día hábil para los anticipos de segunda quincena/mensuales de enero, febrero, mayo, julio y octubre) y **RG CA 2/2026** (BO 18/02/2026).
  - SIRCREB / SIRTAC / SIRCUPA / SIFERE: RG CA 20 a 24/2025 (calendarios 2026); la resolución específica de cada sistema debe confirmarse contra ca.gob.ar.
  - SIRE/SICORE: DDJJ mensual + pago a cuenta quincenal por terminación de CUIT según la agenda oficial de vencimientos ARCA. Aclaración: la RG 5652/2025 fue una prórroga puntual feb-abr 2025 por feriados, no el calendario anual (corrige la referencia del plan de junio).

Fuentes: Boletín Oficial (RG CA 21/2025, Disposición CA 1/2026, RG CA 2/2026, RG ARCA 5652/2025), ca.gob.ar y afip.gob.ar/vencimientos.
