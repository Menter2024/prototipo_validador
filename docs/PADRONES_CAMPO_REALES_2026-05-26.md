# Padrones para pruebas de campo reales — 2026-05-26

## Descargado e integrado

| Jurisdicción | Fuente oficial | Archivo local | Período | Vigencia | Registros | Estado |
|---|---|---|---|---|---:|---|
| Entre Ríos / ATER | https://www.ater.gob.ar/ater2/PadronAlicuotas.asp | `padrones/PadronEntreRios.csv` | 2026-05 | 2026-05-01 a 2026-05-31 | 292163 | aprobado + indexado completo en Supabase |
| CABA / AGIP | https://imagenes.agip.gob.ar/agentes/agentes-de-recaudacion-e-informacion | `padrones/originales/agip_caba_regimenes_generales_2026-06.rar` | 2026-06 | 2026-06-01 a 2026-06-30 | 1598053 en CSV local normalizado; 1000 indexados demo | observado: evidencia completa + índice parcial demo |
| Córdoba / Rentas | https://www.rentascordoba.gob.ar/cms/ca/listados-y-nominas/ | `padrones/originales/cordoba_agentes_iibb_2026-05.pdf` | 2026-05 | 2026-05-01 a 2026-05-31 | 1801 agentes indexados demo | observado: nómina de agentes, no padrón de alícuotas por sujeto |

Evidencias locales:

- Original descargado: `padrones/originales/ater_entrerios_padron_alicuotas_2026-05.pdf`
- CSV normalizado para importación: `padrones/originales/ater_entrerios_padron_alicuotas_2026-05_normalizado.csv`
- Manifest: `padrones/padrones_manifest.json`
- SHA256 normalizado: `84dffa6fc47ffad4e550550cde727d11a2c4a7caad26c5dc7df1f06db793948f`

Nota: el archivo oficial de ATER se descarga con extensión/respuesta tipo PDF, pero su contenido es texto delimitado por `;`. Se normalizaron fechas `DDMMYYYY` a `YYYY-MM-DD` antes de importar para pasar controles de calidad.

## Actualización operativa — 2026-05-27

### Supabase CCU

| Jurisdicción | `padron_version_id` | Estado | Registros | Alcance |
|---|---|---|---:|---|
| Entre Ríos | `5e52ad7d-7b29-491c-8a69-d8c713453ecc` | `activo` | 292163 | índice completo consultable por CUIT |
| CABA | `fa8b0e9d-b6c9-44f8-8cc0-4f3610cc013f` | `observado` | 1000 | muestra real para demo; no usar ausencia como prueba fiscal |
| Córdoba | `533d0251-ebfa-4a25-9abe-160c2f1be108` | `observado` | 1801 | nómina pública de agentes IIBB/recaudación |

CUITs positivos de prueba:

- CABA: `20-00016398-9` (`20000163989`) — aparece en muestra real AGIP con alícuotas 0,00/0,00.
- Córdoba: `30-52999439-3` (`30529994393`) — aparece en nómina pública como agente de percepción.

### CABA / AGIP

- Se descargaron desde fuente oficial los RAR vigentes 01/06/2026:
  - `Padrón de Regímenes Generales - Vigencia 01/06/2026`.
  - `Padrón de Alícuotas Diferenciales Regímenes Particulares - Vigencia 01/06/2026`.
- El RAR de Regímenes Generales se extrajo con `bsdtar` y se normalizó a CSV canónico local con 1598053 registros.
- Por costo/riesgo de cuota del plan gratuito Supabase, no se indexó completo en Postgres: 1,6M filas con JSONB duplicado puede consumir una parte relevante del límite gratuito.
- Se subió el original completo a Supabase Storage privado y se indexó una muestra real de 1000 registros para demo positiva.
- Recomendación MVP: para CABA productivo barato, guardar original completo en Storage y crear índice optimizado sólo con columnas mínimas (`tenant_id`, `provincia`, `cuit`, `ret`, `perc`, `vigencia`) o usar tabla particionada por jurisdicción antes de cargar 1,6M+ filas.

### Córdoba / Rentas

- Se descargaron PDFs oficiales de nóminas vigentes mayo 2026:
  - agentes IIBB;
  - agentes de recaudación IIBB.
- Se extrajeron CUITs con `pdftotext` y se indexó una nómina demo de agentes.
- No debe confundirse con padrón de alícuotas por sujeto pasible: sirve para demostrar condición de agente, no cálculo de retención/percepción a proveedores.

## Ya ubicados localmente, pero no reales vigentes

| Jurisdicción | Archivo | Estado |
|---|---|---|
| Buenos Aires / ARBA | `padrones/PadronARBA.csv` | fixture/demo pequeño; requiere reemplazo por exportación real con CIT/agente |
| CABA / AGIP | `padrones/PadronCABA.csv` | fixture/demo pequeño; el real vigente quedó en `padrones/originales/` y Supabase Storage, no reemplazar en Git |

## Descargables/localizables pero pendientes de importación

| Jurisdicción | Fuente | Estado técnico | Próxima acción |
|---|---|---|---|
| CABA / AGIP | https://imagenes.agip.gob.ar/agentes/agentes-de-recaudacion-e-informacion | Descarga automatizada resuelta con `urllib` porque `curl` local contra AGIP tuvo timeout TLS. | Definir estrategia de índice completo optimizado antes de cargar 1,6M filas a Supabase Free. |
| Jujuy / DPR | https://rentasjujuy.gob.ar/agentes-ingresos-brutos/ | Fuente oficial deriva a formulario GeneXus público para ingresar período y descargar padrón completo. | Automatizar con Playwright o reproducir POST GeneXus; si falla, descarga asistida. |
| Chubut / ARECH | https://www.arech.gob.ar/agentes-de-retencion-y-percepcion/ | Portal SPA oficial guardado como evidencia; el bundle expone múltiples PDFs de normativa/resoluciones, pero no un padrón mensual único normalizado. | Relevar endpoint interno/API del SPA o definirlo como fuente documental/no padrón de alícuotas. |

## Pendientes por credenciales o autorización

| Fuente | Qué necesitamos | Recomendación tributaria-operativa |
|---|---|---|
| ARBA Régimen por Sujeto | CIT o acceso de agente; idealmente CUIT cliente con rol/servicio delegado. | Prioridad máxima para pruebas de campo si el cliente opera en PBA. Sin este padrón, el riesgo de ret/per IIBB PBA queda sólo como potencial. |
| Santa Fe PARP | Clave fiscal ARCA + servicio API Santa Fe/SIAT habilitado; servicio de descarga de padrones/PARP para agentes. | Pedir exportación mensual al cliente/agente como primer paso; automatizar después con consentimiento. Desde RG API 37/2025 el PARP asigna alícuotas de retención/percepción y si el sujeto no figura exige verificar territorialidad y puede aplicar residual. |
| COMARB SIRCREB | Clave fiscal/Portal Federal, perfil agente o contribuyente habilitado. | Crítico para saldos bancarios/recaudaciones. No intentar sin autorización expresa. |
| COMARB SIRCUPA | Idem COMARB; acceso PSP/cuentas de pago según rol. | Relevante para clientes fintech/PSP o proveedores con cobros en billeteras. |
| COMARB SIRCIP/SIRCAR/SIRTAC | Portal Federal/COMARB según régimen. | Empezar por SIRCREB/SIRCUPA; luego SIRCAR/SIRTAC según actividad del cliente. |
| ARCA SIRE | Clave fiscal con servicio SIRE. | Usarlo para evidencia/certificados, no como cálculo de alícuotas inicial. |
| Corrientes / Mendoza / Misiones / Río Negro | Portales con credenciales, navegador o CAPTCHA. | Cola asistida con captura hasta tener adaptación segura. |

## Recomendación para demo de campo

1. Usar `EntreRios` como primera prueba real de padrón masivo: 292163 registros, calidad aprobada, vigencia hasta 2026-05-31.
2. Ejecutar validaciones con CUITs del padrón ATER para demostrar:
   - hallazgo de inscripción en padrón;
   - retención/percepción informada como evidencia, sin cálculo automático;
   - hoja Excel `Regímenes`;
   - manifest de fuente con hash.
3. Para CABA, hacer descarga manual desde navegador oficial AGIP y cargar el RAR en `/padrones` vía UI `/padrones`.
4. Para ARBA/Santa Fe/COMARB, pedir al cliente piloto accesos o exportaciones oficiales. En la demo deben figurar como `pendiente_evidencia` / `no_integrable_cola_asistida`.
5. No commitear los padrones reales; son insumos operativos locales para prueba de campo.
