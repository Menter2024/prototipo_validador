# Roadmap Enterprise

## Fase 1 — MVP fiscal operativo

Estado: mayormente implementado.

- Validación CUIT.
- AFIP/ARCA live.
- Padrones provinciales.
- Importador de padrones.
- Gestión de vigencia e historial.
- Carga masiva Excel/CSV.
- Fuentes online base.
- Neuquén automatizado.
- Motor de decisión fiscal.
- Matriz tributaria inicial.
- Legajo fiscal digital.
- Reporte Excel.

## Fase 2 — Persistencia y seguridad

Prioridad alta para producción real.

- Base de datos PostgreSQL.
- Object Storage para evidencias.
- Autenticación real.
- Roles y permisos.
- Auditoría de acciones.
- Secret manager.
- Backups.
- Separación multiempresa.

## Fase 3 — Workflow tributario

- Estados de proveedor.
- Comentarios del analista.
- Aprobación/rechazo.
- Requerimiento de documentación.
- Revalidación programada.
- Alertas de padrones vencidos. **Base implementada:** `GET /api/fuentes`, `/fuentes` y `scripts/revisar_fuentes.py`.
- Cola de fuentes asistidas. **Base implementada:** `/fuentes-pendientes` con estados, notas, legajo y evidencia.
- Alertas por proveedores bloqueados.

## Fase 4 — Fuentes nacionales ARCA ampliadas

A evaluar e implementar priorizando Web Services oficiales:

- APOC.
- CBU informada.
- Certificados de no retención Ganancias.
- Certificados de no retención IVA.
- Certificados SUSS.
- Agentes de IVA.
- Reproweb u otros servicios aplicables.

## Fase 5 — Automatización provincial/municipal

- Descarga controlada de fuentes públicas. **Base implementada:** `POST /api/fuentes/descargar` y `scripts/descargar_fuentes.py`.
- Circuito por fuente para provincias restantes. **Base implementada:** Córdoba/Jujuy/Tucumán por enlace público; Mendoza/Santa Fe/Corrientes por credenciales; Formosa por archivo cliente; Misiones por navegador; Neuquén por CUIT; Río Negro por CAPTCHA.
- Misiones con navegador/adaptador.
- Río Negro asistido por CAPTCHA.
- Corrientes con credenciales o exportación.
- Municipios relevantes según operación del cliente.
- Evidencias/capturas por fuente.

## Fase 6 — Matriz tributaria avanzada

- Reglas parametrizables.
- Alícuotas por régimen.
- Certificados de exclusión.
- Vigencias.
- Jurisdicción declarada vs domicilio fiscal.
- Convenio multilateral.
- Jurisdicciones IIBB/Convenio Multilateral informadas por constancia ARCA, complementadas con padrones provinciales para inscripciones locales.
- Cálculo sugerido por tipo de operación.

## Fase 7 — Integraciones enterprise

- ERP.
- Cuentas a pagar.
- Maestro de proveedores.
- Google Drive/SharePoint.
- n8n.
- Email/Teams/Slack.
- Exportaciones contables.

## Fase 8 — Producto SaaS / multiempresa

- Tenant por empresa.
- Configuración fiscal por cliente.
- Usuarios y roles por tenant.
- Facturación y límites de uso.
- Observabilidad.
- Soporte y monitoreo.
