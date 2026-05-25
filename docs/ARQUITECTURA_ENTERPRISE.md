# Arquitectura Enterprise — Control Fiscal de Proveedores

## Visión

La solución se diseña como una plataforma de control fiscal para empresas que necesitan operar de forma ordenada frente a obligaciones de retención, percepción e información en Argentina.

Debe evolucionar desde un prototipo funcional hacia una arquitectura enterprise con orquestación de fuentes, reglas tributarias versionadas, evidencia auditable, roles, workflow, integración con ERP, monitoreo y trazabilidad.

## Principios de diseño

### API oficial antes que scraping

Cuando exista Web Service oficial de ARCA, provincia o municipio, debe priorizarse por sobre navegación web.

### Archivo mensual antes que consulta repetitiva

Si una jurisdicción publica padrón mensual, conviene importar y versionar el padrón. Esto reduce fragilidad y mejora la auditoría.

### Navegador automatizado solo donde corresponda

Para fuentes sin API ni archivo mensual puede usarse Playwright/RPA. Si hay CAPTCHA o clave fiscal, la automatización debe ser asistida y no intentar evadir controles.

### Evidencia siempre

Toda decisión debe poder reconstruirse: fuente, fecha, respuesta, usuario, archivo, versión de padrón y regla aplicada.

### Separar dato, regla y decisión

- Dato: respuesta AFIP, padrón, fuente online.
- Regla: criterio tributario configurable.
- Decisión: resultado aplicable al proveedor.

## Componentes actuales

    Frontend HTML
      - Validación individual
      - Carga masiva
      - Administración de padrones
      - Legajos fiscales

    FastAPI
      - /api/validar
      - /api/validar-excel
      - /api/padrones
      - /api/padrones/importar
      - /api/legajos
      - /api/excel

    Módulos fiscales
      - validador CUIT
      - AFIP/ARCA
      - padrones provinciales
      - fuentes online
      - riesgo fiscal
      - matriz tributaria
      - legajos

## Flujo de validación

    Input CUIT(s)
      -> Validación matemática
      -> Consulta AFIP/ARCA
      -> Consulta padrones provinciales
      -> Consulta fuentes online/manuales
      -> Normalización de provincia
      -> Motor de decisión fiscal
      -> Matriz tributaria sugerida
      -> Excel + legajo digital

## Persistencia actual vs futura

### Actual

- CSV para padrones.
- JSON para manifiesto de padrones.
- JSON para legajos.
- XLSX para reportes.
- Archivos locales en salidas, padrones y uploads.

### Recomendado enterprise

- PostgreSQL para legajos, proveedores, estados, usuarios y auditoría.
- Object Storage para evidencias, Excel, PDFs, capturas y archivos originales.
- Secret manager para credenciales fiscales.
- Cola de trabajos para lotes grandes y fuentes lentas.

## Modelo de dominio recomendado

Entidades:

- Empresa cliente
- Usuario
- Rol
- Proveedor
- Validación
- Legajo fiscal
- Fuente fiscal
- Resultado de fuente
- Padrón
- Carga de padrón
- Regla tributaria
- Decisión fiscal
- Matriz de retención/percepción
- Evidencia
- Auditoría

Estados sugeridos de proveedor:

- Pendiente de carga
- Validado automáticamente
- Observado por Impuestos
- Requiere documentación
- Aprobado
- Rechazado
- Revalidación requerida

## Seguridad esperada en producción

- Autenticación real, no Basic Auth.
- Roles: admin, impuestos, compras, cuentas a pagar y auditoría.
- Registro de acciones.
- Cifrado de secretos.
- Separación por empresa/tenant.
- Políticas de retención de evidencia.
- Control de acceso a certificados y claves fiscales.

## Integraciones futuras

- ERP: SAP, Oracle, Tango, Bejerman, Finnegans u otros.
- Google Drive / SharePoint para padrones y legajos.
- Email, Slack o Teams para alertas.
- Supabase/Postgres como persistencia inicial.
- n8n para orquestación externa.
- RPA/Playwright para fuentes sin API.
