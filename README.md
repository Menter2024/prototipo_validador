# Menter — Plataforma de Control Fiscal de Proveedores

Sistema web para automatizar controles fiscales de alta, mantenimiento y revisión de proveedores en empresas medianas y grandes que actúan como agentes de retención, percepción e información dentro del sistema tributario argentino.

El objetivo no es solo consultar CUITs: el producto construye un legajo fiscal digital auditable que ayuda a Compras, Cuentas a Pagar, Impuestos, Compliance y Auditoría a decidir si un proveedor es aprobable, observado, requiere revisión manual o debe bloquearse.

Estado actual: prototipo funcional desplegable con AFIP/ARCA live, padrones provinciales, monitor de fuentes, fuentes online, carga masiva, matriz tributaria inicial, motor de decisión fiscal y legajos digitales.

## Problema que resuelve

Las compañías con volumen relevante de proveedores deben administrar obligaciones formales y operativas vinculadas a:

- alta fiscal de proveedores;
- validación de CUIT, inscripción y condición tributaria;
- padrones de retención/percepción provinciales;
- certificados, exclusiones, CBU y constancias;
- controles de riesgo fiscal y facturación apócrifa;
- evidencia para auditoría interna, externa o fiscal;
- actualización mensual de padrones;
- coordinación entre Compras, Impuestos y Cuentas a Pagar.

El sistema centraliza este proceso y reduce controles manuales dispersos en planillas, capturas y portales.

## Usuarios objetivo

- Impuestos: define criterios, administra padrones y revisa observaciones.
- Compras / Abastecimiento: inicia altas y consulta estado.
- Cuentas a Pagar: controla antes de pagar.
- Compliance: revisa señales críticas.
- Auditoría: consulta legajos, evidencias e historial.
- Sistemas / Data: integra ERP, almacenamiento y automatizaciones.

## Capacidades implementadas

### Validación fiscal de CUIT

- Validación matemática del dígito verificador.
- Normalización de CUIT/CUIL con o sin guiones.
- Clasificación básica de tipo de persona.

Módulo: app/modules/validador.py

### Consulta AFIP/ARCA live

- Integración vía AFIPSDK.
- Soporte productivo con certificado y clave.
- Credenciales por variables de entorno, PEM directo o base64.
- Razón social, estado, actividad, domicilio, IVA, Ganancias y monotributo.

Módulo: app/modules/afip_arca.py

### Padrones provinciales de Ingresos Brutos

Padrones por archivo mensual:

- ARBA / Buenos Aires
- CABA / AGIP
- Entre Ríos / ATER
- Córdoba
- Formosa
- Jujuy
- Mendoza
- Santa Fe
- Tucumán

Fuentes sin archivo mensual normalizado:

- Misiones
- Neuquén
- Río Negro
- Corrientes

Módulos: app/modules/padrones.py y app/modules/padron_manifest.py

### Importador y lifecycle de padrones

- CSV, TXT, TSV, PSV, XLSX y XLSM.
- Separadores coma, punto y coma, tab y pipe.
- UTF-8 y Latin-1.
- Alias de columnas y deduplicación de CUIT.
- Backup automático antes de sobrescribir.
- Período, vigencia, historial y estado de vigencia.

CLI: scripts/importar_padron.py
Web: /padrones

### Fuentes online sin padrón mensual

- Neuquén automatizado contra endpoint público.
- Misiones modelado como requiere navegador/adaptador por bloqueo 403.
- Río Negro modelado como requiere CAPTCHA.
- Corrientes modelado como requiere credenciales.

Módulo: app/modules/fuentes_online.py

### Monitor de fuentes y calendario operativo

- Catálogo versionado de fuentes nacionales/provinciales.
- Clasificación por API oficial, padrón descargable, consulta online, CAPTCHA o credenciales.
- Estado de actualización: vigente, por vencer, vencido, pendiente de carga o asistido.
- Riesgo operativo por prioridad P0/P1/P2/P3.
- API y pantalla para alertas de padrones críticos.
- Script apto para scheduler diario.

Config: config/fuentes_catalogo.json
Web: /fuentes
API: /api/fuentes
CLI: scripts/revisar_fuentes.py

### Motor de decisión fiscal

Estados:

- APROBABLE
- OBSERVADO
- REVISIÓN MANUAL
- BLOQUEAR

Evalúa CUIT inválido, AFIP/ARCA, estado fiscal, APOC, monotributo, padrones IIBB, fuentes pendientes y hallazgos online.

Módulo: app/modules/riesgo_fiscal.py

### Matriz tributaria inicial

Consolida señales para retenciones/percepciones:

- IVA nacional;
- Ganancias nacional;
- IIBB por jurisdicción;
- alícuotas de retención/percepción informadas por padrones;
- alertas por padrones faltantes;
- alertas por fuentes manuales;
- advertencias por monotributo.

Módulo: app/modules/matriz_tributaria.py

### Carga masiva desde Excel/CSV

- XLSX, XLSM, CSV, TXT, TSV y PSV.
- Detección automática de columna CUIT/CUIL.
- Columna y hoja opcionales.
- Deduplicación.
- Límite inicial: 500 CUITs por lote.
- Excel consolidado y legajo del lote.

Web: /lotes
Módulo: app/modules/carga_masiva.py

### Legajo fiscal digital

Cada validación genera evidencia auditable:

- ID único;
- fecha/hora;
- CUIT y razón social;
- decisión fiscal;
- motivos y recomendaciones;
- AFIP/ARCA;
- padrones;
- fuentes online;
- matriz tributaria;
- Excel asociado;
- JSON completo de evidencia.

Web: /legajos y /legajos/{id}
Módulo: app/modules/legajos.py

### Reportes Excel

Hojas generadas:

- Resumen
- AFIP-ARCA
- Padrones IIBB
- Fuentes online
- Matriz tributaria
- Trazabilidad

Módulo: app/modules/excel.py

## Pantallas principales

| Ruta | Uso |
|---|---|
| / | Validación individual o múltiple por texto |
| /lotes | Carga masiva desde Excel/CSV |
| /padrones | Administración de padrones provinciales |
| /fuentes | Monitor de fuentes fiscales y alertas |
| /legajos | Historial de legajos fiscales |
| /legajos/{id} | Detalle y evidencia de un legajo |
| /api/info | Diagnóstico no sensible |
| /healthz | Health check |

## Arquitectura técnica

Stack actual:

- Python 3.11+
- FastAPI
- HTML + Tailwind CDN
- OpenPyXL
- HTTPX
- Render/Railway compatible
- Persistencia local en archivos para prototipo

Estructura:

    app/main.py
    app/modules/afip_arca.py
    app/modules/validador.py
    app/modules/padrones.py
    app/modules/padron_manifest.py
    app/modules/fuentes_catalogo.py
    app/modules/fuentes_online.py
    app/modules/riesgo_fiscal.py
    app/modules/matriz_tributaria.py
    app/modules/carga_masiva.py
    app/modules/legajos.py
    app/modules/excel.py
    scripts/importar_padron.py
    scripts/revisar_fuentes.py
    config/fuentes_catalogo.json
    padrones/
    salidas/
    docs/

## Variables de entorno

    AFIPSDK_TOKEN=
    AFIPSDK_ENV=prod
    AFIPSDK_TAX_ID=
    AFIPSDK_CERT_PEM=
    AFIPSDK_KEY_PEM=
    AFIPSDK_CERT_B64=
    AFIPSDK_KEY_B64=
    BASIC_AUTH_USER=
    BASIC_AUTH_PASS=
    PADRONES_DIR=./padrones
    SALIDAS_DIR=./salidas
    UPLOADS_DIR=./uploads

## Instalación local

    bash run.sh

Luego abrir http://localhost:8000.

## Deploy

El repo incluye render.yaml para Render. El sitio queda protegido con Basic Auth. /healthz y /api/info quedan públicos para health check y diagnóstico no sensible.

## Consideraciones de compliance

El sistema es una plataforma de asistencia, control y evidencia. No reemplaza el criterio profesional de Impuestos ni la liquidación definitiva de retenciones/percepciones.

Para producción enterprise se debe agregar:

- persistencia real;
- usuarios y roles;
- auditoría de acciones;
- gestión segura de secretos;
- cifrado y backups;
- monitoreo;
- validación formal de reglas tributarias;
- revisión legal/fiscal de fuentes automatizadas.

## Documentación complementaria

- docs/ARQUITECTURA_ENTERPRISE.md
- docs/OPERACION_TRIBUTARIA.md
- docs/ROADMAP_ENTERPRISE.md
- docs/AUTOMATIZACION_PADRONES.md
- docs/ANTECEDENTES_FUENTES.md
- padrones/README.md
