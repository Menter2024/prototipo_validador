# Manual de Usuario — Menter Fiscal

## 1. Objetivo

Menter Fiscal permite validar proveedores antes del alta, pago o revisión periódica. El sistema consulta CUITs, cruza fuentes fiscales, genera una decisión sugerida y conserva evidencia en un legajo auditable.

La decisión final sigue siendo responsabilidad del equipo fiscal/compliance de la empresa.

## 2. Roles recomendados

| Rol | Uso principal |
|---|---|
| Compras | Consulta rápida de proveedores y revisión de decisión sugerida. |
| Cuentas a Pagar | Validación masiva antes de pagos y descarga de Excel. |
| Impuestos | Configuración, padrones, fuentes, accesos y revisión de observados. |
| Auditoría | Revisión de legajos, evidencia, trazabilidad y reportes. |
| Admin técnico | Diagnóstico, despliegue, variables y monitoreo. |

## 3. Flujo recomendado de operación

1. Entrar a **Dashboard** para revisar estado general.
2. Completar **Configuración** del cliente y cobertura fiscal.
3. Cargar o actualizar **Padrones** críticos.
4. Registrar **Accesos** fiscales necesarios.
5. Validar proveedores desde **Consultar** o **Carga masiva**.
6. Revisar decisiones y descargar **Excel** o **Legajo**.
7. Atender pendientes en **Cola asistida**.
8. Consultar **Legajos** para auditoría o comparación histórica.

## 4. Dashboard

Ruta: `/dashboard`

### Para qué sirve

Muestra una vista ejecutiva del piloto:

- cantidad de legajos;
- proveedores evaluados;
- aprobables;
- observados;
- bloqueados;
- estado de storage local/Supabase;
- salud operativa de padrones, fuentes y accesos.

### Cómo usarlo

1. Abrir **Dashboard**.
2. Seleccionar el rol desde **Vista por rol**.
3. Revisar los KPIs superiores.
4. Mirar la distribución de riesgo.
5. Ejecutar las próximas acciones sugeridas.
6. Abrir últimos legajos si se necesita evidencia.

### Interpretación rápida

| Indicador | Qué significa | Acción |
|---|---|---|
| Aprobables | Proveedores sin observación crítica. | Continuar proceso interno. |
| Observados | Requieren revisión o documentación. | Derivar a Impuestos. |
| Bloqueados | Señales críticas. | No aprobar sin análisis fiscal/compliance. |
| Alertas de fuentes | Fuentes vencidas/faltantes. | Ir a Fuentes o Padrones. |
| Accesos pendientes | Faltan autorizaciones/exportaciones. | Ir a Accesos. |

## 5. Configuración guiada

Ruta: `/configuracion`

### Objetivo

Dejar listo el piloto para operar con un cliente o grupo económico.

### Paso a paso

1. Abrir **Config.**.
2. Completar **Cliente / grupo económico**.
3. Completar **CUITs agente** separados por coma.
4. Marcar **Jurisdicciones prioritarias**.
5. Tocar **Guardar configuración local**.
6. Revisar el **score de cobertura fiscal**.
7. Completar las acciones del checklist:
   - activar ARCA live si corresponde;
   - cargar padrones prioritarios;
   - resolver accesos fiscales;
   - atender alertas operativas.

### Score de cobertura

| Score | Estado | Interpretación |
|---|---|---|
| 85% o más | Alta | Listo para piloto controlado. |
| 60% a 84% | Media | Operable, pero con pendientes. |
| Menos de 60% | Inicial | Requiere configuración antes de uso real. |

Nota: la configuración de esta pantalla se guarda en el navegador. Para producción se debe persistir por tenant/cliente.

## 6. Consulta rápida de proveedores

Ruta: `/`

### Cuándo usarla

Para validar uno o pocos CUITs antes del alta o revisión puntual.

### Paso a paso

1. Abrir **Consultar**.
2. Pegar uno o varios CUITs, uno por línea o separados por coma/punto y coma.
3. Tocar **Validar**.
4. Esperar la consulta de fuentes.
5. Revisar la tarjeta de decisión.
6. Ejecutar la próxima acción sugerida.
7. Descargar Excel o abrir el legajo.

### Decisiones posibles

| Decisión | Significado | Acción recomendada |
|---|---|---|
| Aprobable | No se detectaron señales críticas. | Continuar alta/pago según política interna. |
| Observado | Hay datos incompletos o hallazgos moderados. | Revisar documentación o padrones. |
| Requiere revisión | Falta evidencia o fuente manual. | Derivar a Impuestos. |
| Bloquear | Riesgo alto o inconsistencia crítica. | No aprobar sin análisis formal. |

### Detalles disponibles

Cada resultado incluye acordeones:

- resumen fiscal y ARCA;
- padrones y fuentes oficiales;
- obligaciones y matriz tributaria;
- evidencia técnica dentro del legajo.

## 7. Carga masiva

Ruta: `/lotes`

### Cuándo usarla

Para revisar un archivo Excel/CSV con varios proveedores.

### Paso a paso

1. Abrir **Carga masiva**.
2. Subir archivo `.xlsx`, `.xlsm`, `.csv`, `.txt`, `.tsv` o `.psv`.
3. Si el sistema no detecta la columna, completar **Columna opcional** con el nombre de la columna CUIT.
4. Si es Excel y hace falta, completar **Hoja XLSX opcional**.
5. Tocar **Validar lote**.
6. Descargar Excel o abrir el legajo generado.

### Buenas prácticas

- Mantener una columna clara llamada `CUIT`, `CUIL` o similar.
- Evitar archivos con múltiples tablas mezcladas.
- Validar primero un lote chico si se está probando una fuente nueva.

## 8. Padrones

Ruta: `/padrones`

### Objetivo

Cargar padrones oficiales provinciales para cruzar retenciones/percepciones de Ingresos Brutos.

### Paso a paso

1. Abrir **Operación → Padrones**.
2. Arrastrar el archivo oficial o hacer click para seleccionarlo.
3. Revisar autodetección:
   - provincia;
   - período;
   - vigencia hasta;
   - fuente oficial asociada.
4. Corregir manualmente si la detección no es correcta.
5. Tocar **Previsualizar**.
6. Revisar:
   - registros válidos;
   - descartados;
   - duplicados;
   - layout detectado;
   - advertencias.
7. Si todo es correcto, tocar **Importar padrón**.
8. Revisar cards de estado y vigencia.

### Advertencias

- Si hay advertencias de calidad, el sistema pedirá confirmación antes de sobrescribir.
- Para archivos grandes, especialmente padrones reales provinciales, puede convenir carga asistida/background o infraestructura con más recursos.
- No subir padrones reales a Git.

## 9. Fuentes

Ruta: `/fuentes`

### Objetivo

Monitorear fuentes oficiales, vigencias, riesgos y descargas.

### Cómo usarla

1. Abrir **Operación → Fuentes**.
2. Revisar KPIs y alertas operativas.
3. Priorizar fuentes P0/P1 vencidas o sin carga.
4. Usar **relevar** para detectar candidatos de descarga.
5. Usar **descargar** cuando la fuente sea pública y automatizable.
6. Si una fuente requiere CAPTCHA, credenciales o navegador, atenderla desde **Cola asistida**.

## 10. Accesos fiscales

Ruta: `/accesos`

### Objetivo

Registrar autorizaciones, exportaciones manuales, usuario técnico o evidencia de acceso.

### Paso a paso

1. Abrir **Operación → Accesos**.
2. Revisar **Pendientes prioritarios**.
3. Tocar **Usar en formulario** para precompletar desde una fuente crítica.
4. Completar:
   - cliente;
   - CUIT agente;
   - organismo;
   - servicio;
   - tipo de acceso;
   - estado;
   - responsable;
   - alcance;
   - notas;
   - evidencia.
5. Tocar **Guardar acceso**.
6. Verificar que el acceso figure como registrado.

### Reglas de seguridad

- No cargar claves personales en notas.
- Registrar sólo evidencia, autorización o modalidad de acceso.
- Usar usuario técnico/delegado cuando corresponda.
- Mantener responsable y alcance claros.

## 11. Cola asistida

Ruta: `/fuentes-pendientes`

### Objetivo

Resolver tareas que no pudieron automatizarse: CAPTCHA, credenciales, navegador asistido o revisión manual.

### Paso a paso

1. Abrir **Operación → Cola asistida**.
2. Filtrar por estado:
   - Todas;
   - Pendientes;
   - En proceso;
   - Resueltas.
3. Revisar edad/SLA de cada card.
4. Abrir fuente o legajo si está disponible.
5. Cambiar estado.
6. Agregar nota o evidencia.
7. Tocar **Guardar avance**.

### Estados

| Estado | Uso |
|---|---|
| Pendiente | Todavía no fue trabajada. |
| En proceso | Hay responsable trabajando. |
| Resuelta | La evidencia o consulta fue completada. |
| Descartada | No aplica al caso. |
| Error | Hubo bloqueo técnico u operativo. |

## 12. Legajos

Ruta: `/legajos`

### Objetivo

Consultar historial auditable de validaciones.

### Cómo usarlo

1. Abrir **Legajos**.
2. Buscar por CUIT o razón social.
3. Filtrar por decisión si hace falta.
4. Revisar KPIs.
5. Abrir un legajo.
6. Descargar Excel si se requiere soporte documental.

### Comparación histórica

Al buscar un CUIT, la pantalla muestra validaciones anteriores para comparar evolución de decisión, fecha y evidencia.

## 13. Detalle de legajo

Ruta: `/legajos/{id}`

### Contenido

- timeline de auditoría;
- KPIs del legajo;
- decisión por proveedor;
- próxima acción;
- motivos;
- recomendaciones;
- evidencia resumida;
- JSON técnico completo;
- Excel asociado.

### Exportar PDF

1. Abrir el legajo.
2. Tocar **Imprimir / PDF**.
3. Elegir destino PDF en el navegador.
4. Guardar el archivo según política interna.

## 14. Diagnóstico técnico

Ruta: `/info`

Usar sólo para revisión técnica o soporte. Muestra:

- modo AFIP/ARCA;
- carpetas configuradas;
- padrones detectados;
- estado Supabase;
- alertas básicas.

## 15. Operación diaria sugerida

### Al inicio del día

1. Abrir Dashboard.
2. Revisar bloqueados y observados.
3. Revisar alertas de fuentes.
4. Revisar cola asistida pendiente.

### Antes de aprobar un proveedor

1. Consultar CUIT.
2. Revisar decisión.
3. Abrir legajo.
4. Descargar Excel o PDF si la política lo requiere.
5. Registrar cualquier revisión manual en la cola o en el circuito interno.

### Antes de cierres mensuales

1. Revisar Padrones.
2. Actualizar fuentes vencidas o por vencer.
3. Resolver accesos pendientes.
4. Ejecutar validación masiva de proveedores críticos.

## 16. Errores frecuentes

| Situación | Causa probable | Solución |
|---|---|---|
| CUIT inválido | Dígito verificador incorrecto. | Corregir CUIT. |
| Fuente no cargada | Falta padrón o integración. | Ir a Padrones/Fuentes. |
| Requiere credenciales | Fuente no es pública. | Registrar acceso autorizado. |
| Requiere CAPTCHA | No automatizable completamente. | Resolver desde Cola asistida. |
| Archivo grande falla | Límite de hosting demo. | Usar carga asistida/background o infraestructura mayor. |
| No hay ARCA live | Falta token/certificado. | Revisar Diagnóstico técnico. |

## 17. Buenas prácticas

- Mantener padrones vigentes.
- Documentar todo acceso fiscal con responsable y alcance.
- No guardar claves personales en el sistema.
- Descargar legajo/Excel para soportes relevantes.
- Usar cola asistida para no perder tareas manuales.
- Revisar bloqueados antes de aprobaciones.
- No considerar “sin hallazgo” como verdad absoluta si una fuente está vencida o no cargada.

## 18. Límites del prototipo

- La decisión es sugerida, no reemplaza criterio profesional.
- Algunas fuentes pueden estar en modo demo/fallback.
- PDF es impresión del navegador, no render server-side.
- Configuración guiada usa almacenamiento local del navegador.
- Para producción se recomienda persistencia multiusuario, RBAC, auditoría completa y gestión segura de secretos.
