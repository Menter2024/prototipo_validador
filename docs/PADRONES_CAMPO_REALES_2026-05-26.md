# Padrones para pruebas de campo reales — 2026-05-26

## Descargado e integrado

| Jurisdicción | Fuente oficial | Archivo local | Período | Vigencia | Registros | Estado |
|---|---|---|---|---|---:|---|
| Entre Ríos / ATER | https://www.ater.gob.ar/ater2/PadronAlicuotas.asp | `padrones/PadronEntreRios.csv` | 2026-05 | 2026-05-01 a 2026-05-31 | 292163 | aprobado |

Evidencias locales:

- Original descargado: `padrones/originales/ater_entrerios_padron_alicuotas_2026-05.pdf`
- CSV normalizado para importación: `padrones/originales/ater_entrerios_padron_alicuotas_2026-05_normalizado.csv`
- Manifest: `padrones/padrones_manifest.json`
- SHA256 normalizado: `84dffa6fc47ffad4e550550cde727d11a2c4a7caad26c5dc7df1f06db793948f`

Nota: el archivo oficial de ATER se descarga con extensión/respuesta tipo PDF, pero su contenido es texto delimitado por `;`. Se normalizaron fechas `DDMMYYYY` a `YYYY-MM-DD` antes de importar para pasar controles de calidad.

## Ya ubicados localmente, pero no reales vigentes

| Jurisdicción | Archivo | Estado |
|---|---|---|
| Buenos Aires / ARBA | `padrones/PadronARBA.csv` | fixture/demo pequeño; requiere reemplazo por exportación real con CIT/agente |
| CABA / AGIP | `padrones/PadronCABA.csv` | fixture/demo pequeño; parser existe, pero no se pudo descargar archivo real desde la red local |

## Descargables/localizables pero pendientes de importación

| Jurisdicción | Fuente | Estado técnico | Próxima acción |
|---|---|---|---|
| CABA / AGIP | https://imagenes.agip.gob.ar/agentes/agentes-de-recaudacion-e-informacion | La página oficial publica `Padrón de Regímenes Generales - Vigencia 01/06/2026` y `Padrón de Alícuotas Diferenciales - Vigencia 01/06/2026`. El intento local por `curl` contra AGIP terminó en timeout TLS. | Descargar manualmente desde navegador o probar desde otra red/VPN; luego importar con parser CABA RAR/TXT ya existente. |
| Jujuy / DPR | https://rentasjujuy.gob.ar/agentes-ingresos-brutos/ | Fuente oficial deriva a formulario GeneXus público para ingresar período y descargar padrón completo. | Automatizar con Playwright o reproducir POST GeneXus; si falla, descarga asistida. |
| Chubut / ARECH | https://www.arech.gob.ar/agentes-de-retencion-y-percepcion/ | Portal SPA oficial guardado como evidencia; el bundle expone múltiples PDFs de normativa/resoluciones, pero no un padrón mensual único normalizado. | Relevar endpoint interno/API del SPA o definirlo como fuente documental/no padrón de alícuotas. |

## Pendientes por credenciales o autorización

| Fuente | Qué necesitamos | Recomendación tributaria-operativa |
|---|---|---|
| ARBA Régimen por Sujeto | CIT o acceso de agente; idealmente CUIT cliente con rol/servicio delegado. | Prioridad máxima para pruebas de campo si el cliente opera en PBA. Sin este padrón, el riesgo de ret/per IIBB PBA queda sólo como potencial. |
| Santa Fe PARP | Clave fiscal ARCA + servicio API Santa Fe/SIAT habilitado. | Pedir exportación mensual al cliente/agente como primer paso; automatizar después con consentimiento. |
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
