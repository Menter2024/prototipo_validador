# Operación tributaria — Uso por áreas fiscales

## Objetivo operativo

Dar soporte a empresas que deben controlar formalidades fiscales antes de dar de alta, pagar o mantener proveedores.

La solución ayuda a responder:

- ¿El CUIT es válido?
- ¿El proveedor existe y está activo ante ARCA?
- ¿Cuál es su condición frente a IVA, Ganancias o Monotributo?
- ¿Figura en padrones de IIBB?
- ¿Qué alícuotas de retención/percepción aparecen?
- ¿Hay fuentes pendientes de CAPTCHA, clave o revisión manual?
- ¿Conviene aprobar, observar, bloquear o derivar a Impuestos?
- ¿Qué evidencia queda guardada?

## Proceso sugerido de alta de proveedor

1. Compras carga CUIT o lote Excel.
2. El sistema valida CUIT y consulta fuentes automáticas.
3. Impuestos revisa decisión fiscal sugerida.
4. Si hay observaciones, solicita documentación o completa fuentes manuales.
5. Se genera legajo fiscal digital.
6. Se exporta Excel para respaldo o integración.
7. El proveedor pasa a aprobado, observado o bloqueado.

## Padrones provinciales

Responsabilidad de Impuestos:

- Descargar padrones mensuales oficiales.
- Cargarlos desde la pantalla /padrones.
- Informar período y vigencia.
- Revisar estado de vigencia.
- Revalidar proveedores cuando se actualicen padrones.

Controles implementados:

- Backup antes de sobrescribir.
- Historial de cargas.
- Registros importados.
- Período.
- Vigencia hasta.
- Estado: vigente, por vencer, vencido o sin vigencia.

## Fuentes online/manuales

Automatizada:

- Neuquén: consulta automática contra endpoint público.

Asistidas o pendientes:

- Misiones: requiere navegador/adaptador por bloqueo de endpoint directo.
- Río Negro: requiere CAPTCHA o consulta asistida.
- Corrientes: requiere credenciales o exportación.

Criterio operativo: cuando una fuente no puede consultarse automáticamente, no debe marcarse como no inscripto. Debe figurar como pendiente, asistida o con credenciales.

## Motor de decisión fiscal

| Estado | Uso |
|---|---|
| APROBABLE | Sin observaciones críticas con la información disponible |
| OBSERVADO | Requiere atención fiscal, pero no necesariamente bloqueo |
| REVISIÓN MANUAL | Hay fuentes pendientes, demo/fallback o evidencia incompleta |
| BLOQUEAR | Riesgo crítico o inconsistencia que impide avanzar |

Ejemplos:

- CUIT inválido: BLOQUEAR.
- AFIP no activo: BLOQUEAR.
- Monotributista: OBSERVADO.
- Figura en IIBB: OBSERVADO por aplicación de alícuotas.
- Faltan padrones: OBSERVADO.
- Fuente con CAPTCHA pendiente: REVISIÓN MANUAL.

## Matriz tributaria

La matriz tributaria no reemplaza la liquidación final. Consolida señales para Impuestos:

- condición IVA;
- condición Ganancias;
- IIBB por jurisdicción;
- alícuotas de retención/percepción;
- alertas por falta de padrón;
- alertas por fuentes manuales;
- advertencias por monotributo.

Debe evolucionar hacia reglas parametrizables por empresa, régimen y jurisdicción.

## Legajo fiscal digital

Contiene:

- fecha/hora;
- proveedor;
- fuentes consultadas;
- decisión fiscal;
- motivos;
- recomendaciones;
- matriz tributaria;
- Excel asociado;
- evidencia JSON completa.

En producción debe guardarse en almacenamiento persistente, con control de usuario y auditoría.

## Buenas prácticas para empresas

- Revalidar proveedores críticos antes de pagos relevantes.
- Definir frecuencia de revalidación por riesgo.
- Mantener vigentes padrones mensuales.
- No aprobar altas con AFIP demo/fallback.
- No tratar fuentes pendientes como resultado negativo.
- Guardar evidencia de cada decisión.
- Versionar reglas tributarias internas.
