# Piloto CCU — Readiness Checklist

## Objetivo

Dejar el prototipo Menter Fiscal listo para una prueba piloto real con usuarios de CCU, minimizando fricción operativa y evitando conclusiones fiscales erróneas por falta de datos, fuentes o accesos.

## Estado general

La aplicación ya tiene la base funcional para piloto:

- consulta individual y masiva de proveedores;
- dashboard ejecutivo;
- configuración guiada;
- carga y control de padrones;
- monitor de fuentes;
- accesos fiscales;
- cola asistida;
- legajos auditables;
- Excel y PDF por impresión;
- manual de usuario en `/manual`.

Lo que falta para estar ideal no es mayormente desarrollo visual, sino **preparación operativa y datos reales controlados**.

## Checklist mínimo para piloto

| Área | Requisito | Estado esperado |
|---|---|---|
| Usuarios | Definir 3 a 5 usuarios CCU por rol | Pendiente de CCU |
| CUITs CCU | Confirmar sociedades/CUIT agente del grupo | Pendiente de CCU |
| Proveedores piloto | Archivo con 20 a 50 CUITs reales de prueba | Pendiente de CCU |
| ARCA | Confirmar si se usará live o demo/fallback | Pendiente/configurable |
| Padrones | Cargar CABA, ARBA, Córdoba y Santa Fe prioritarios | Parcial/operativo |
| Supabase | Confirmar Storage + índice compacto o demo parcial | Decisión técnica/comercial |
| Accesos | Registrar fuentes que requieren credencial/exportación | Pendiente operativo |
| Seguridad | Confirmar Basic Auth y no exponer service_role | Requerido |
| Evidencia | Validar Excel, legajo y PDF imprimible | Disponible |
| Aceptación | Definir criterios de éxito del piloto | Pendiente negocio |

## Datos que hay que pedir a CCU

1. Lista de usuarios piloto:
   - nombre;
   - email;
   - área;
   - rol esperado: Compras, Cuentas a Pagar, Impuestos, Auditoría o Admin.
2. CUITs agente/sociedades del grupo que participarán.
3. Lista de proveedores de prueba:
   - CUIT;
   - razón social esperada;
   - criticidad o volumen;
   - jurisdicción esperada si se conoce.
4. Padrones o exportaciones disponibles desde portales fiscales.
5. Fuentes con acceso delegado o usuario técnico.
6. Criterios internos de aprobación/bloqueo.
7. Formato deseado para entregar evidencias: Excel, PDF, link de legajo o todos.

## Configuración recomendada para piloto

### Infraestructura

- Backend FastAPI actual.
- Basic Auth activo.
- Supabase habilitado para Storage y metadata.
- No exponer claves en frontend.
- Mantener padrones reales fuera de Git.

### Supabase

Para piloto ideal:

1. Subir originales completos a Storage.
2. Guardar metadata en `padron_versiones`.
3. Indexar sólo registros necesarios para consulta rápida:
   - proveedores del piloto;
   - jurisdicciones prioritarias;
   - o tabla compacta completa si se decide plan Pro.

No se recomienda guardar padrones completos como JSONB pesado en Free.

### Padrones prioritarios

1. CABA / AGIP.
2. Buenos Aires / ARBA.
3. Córdoba.
4. Santa Fe.
5. COMARB/SIRCREB si CCU lo considera crítico.

## Flujo de prueba sugerido

### Día 0 — Preparación

1. Confirmar usuarios y roles.
2. Confirmar URL y credenciales Basic Auth.
3. Cargar configuración guiada.
4. Cargar padrones disponibles.
5. Registrar accesos pendientes.
6. Ejecutar lote piloto interno.
7. Revisar dashboard y legajos.

### Día 1 — Demo guiada

1. Mostrar dashboard.
2. Validar un proveedor aprobable.
3. Validar un proveedor observado.
4. Validar un CUIT con fuente pendiente/manual.
5. Mostrar legajo y Excel.
6. Mostrar cola asistida.
7. Mostrar actualización de padrón.

### Semana 1 — Piloto operativo

1. CCU carga lote de proveedores.
2. Impuestos revisa observados/bloqueados.
3. Se cierran tareas asistidas.
4. Se documentan falsos positivos/negativos.
5. Se ajusta criterio fiscal y fuentes prioritarias.

## Criterios de éxito

| Métrica | Meta inicial |
|---|---:|
| Usuarios activos piloto | 3 a 5 |
| Proveedores evaluados | 20 a 50 |
| Legajos generados | 100% de consultas |
| Excel descargable | 100% de lotes |
| Observados con motivo claro | 100% |
| Fuentes faltantes identificadas | 100% |
| Tiempo por consulta individual | Menos de 30 segundos salvo fuente externa lenta |
| Sin exposición de datos sensibles en Git | 100% |

## Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Padrón real muy grande | Storage + índice compacto/parcial o Pro. |
| Fuente con CAPTCHA | Cola asistida y evidencia manual. |
| ARCA no live | Marcar demo/fallback y no aprobar en piloto real. |
| Usuarios no técnicos confundidos | Usar Dashboard, Manual y flujo guiado. |
| Falso “no inscripto” por fuente faltante | Mostrar observado/fuente no cargada, nunca negativo definitivo. |
| Datos reales en Git | Mantener `.gitignore`, no stagear `padrones/`. |

## Qué puedo hacer desde el proyecto

Puedo dejar preparado:

- página `/piloto-ccu` con checklist vivo;
- documentación versionada;
- checklist de datos requeridos a CCU;
- flujo de prueba;
- validaciones de readiness con APIs existentes;
- mejoras de UX/operación;
- commit y push de cambios de código/documentación.

## Qué requiere input externo

No puedo completar sin CCU o credenciales:

- usuarios reales;
- CUITs agente definitivos;
- proveedor/lote real de prueba;
- credenciales o exportaciones fiscales;
- decisión comercial Supabase Free/Pro;
- acceso MCP/keys válidas si se quiere operar Supabase remotamente desde Codex.
