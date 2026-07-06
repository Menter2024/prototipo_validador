# Nota para Luis Ronchi — Documentación recibida y pendientes

**Fecha:** 2026-07-03
**De:** Menter S.A.S.
**Para:** Luis Ronchi — Impuestos CICSA/CCU
**Referencia:** Carpeta "Constancias impositivas vigentes CICSA" (29 documentos) recibida y procesada. Complementa el pedido original de [PEDIDO_DATOS_CCU_IMPUESTOS.md](PEDIDO_DATOS_CCU_IMPUESTOS.md).

## Lo que ya quedó resuelto con la carpeta recibida — gracias

Con lo que mandaste quedaron **confirmadas documentalmente** las designaciones de agente en: **IVA nacional** (RG 608/99 desde 07/1999), **Ganancias RG 830 vía SICORE** (regímenes desde 2000), **SUSS** (6 regímenes), **beneficiarios del exterior** (8 regímenes), **API Santa Fe** (ret. + perc.), **AGIP CABA** (recaudación desde 09/2001), **Rentas Córdoba** (ret./perc. N° 300023711), **ATER Entre Ríos** (retención), **ATM Mendoza** (perc. 2015 + ret. 2020), **DPR Neuquén** (percepción, SIRCAR), **DGR Santiago del Estero** (percepción, SIRCAR), **DPIP San Luis** (percepción por encuadre RG 16-DPIP-2007) y **Municipalidad de Córdoba** (retención contribución comercial desde 11/2016). También la constancia CM que acredita inscripción en las **24 jurisdicciones** y los certificados propios de exclusión/no retención.

Todo quedó cargado en la plataforma con su archivo como evidencia.

## Actualización 2026-07-06 — cómo proponemos la prueba, y una aclaración importante

**La prueba la manejás vos, con tus datos.** La idea es simple: te damos usuario propio (con tu rol) y probás el circuito completo como lo harías en tu operación diaria:

1. **Cargás el padrón del mes** de una jurisdicción donde CICSA es agente (por ejemplo el de ARBA o AGIP que ya usan para liquidar) desde la pantalla de padrones — con previsualización, control de calidad y evidencia automática.
2. **Cargás una tanda de CUITs reales de proveedores** (individual o por Excel) y el sistema devuelve: situación ARCA en vivo, cruce contra los padrones que cargaste, decisión sugerida (aprobable/observado/revisión/bloquear), matriz de señales y el legajo sellado con toda la evidencia.
3. **Comparás contra lo que Impuestos ya sabe** de esos proveedores y nos marcás dónde el sistema acierta, dónde le falta y qué criterio propio de CICSA habría que configurar.

**Aclaración importante sobre credenciales ARCA** (corrige el punto 16 de esta nota): **no necesitamos ningún certificado ni clave fiscal de CICSA para la consulta de constancias** — eso corre con el certificado digital propio de Menter, porque el web service de constancia consulta datos de terceros. Lo que sí necesitamos de ustedes es solo esto:

- **Los archivos de padrón de agente** que descargan de los portales provinciales (o, si prefieren, acceso delegado al portal para descargarlos nosotros): esos archivos solo los puede bajar el agente designado.
- Más adelante, si el sistema tuviera que actuar en nombre de CICSA (Mis Retenciones, SIRE/SICORE): **delegación formal de servicios vía "Administrador de Relaciones" de ARCA** al CUIT de Menter — trámite auditable y revocable. **Nunca vamos a pedir contraseñas.**

## Lo que falta — punto por punto

### A. Designaciones de agente sin documento (lo más importante)

1. **ARBA / Buenos Aires**: no vino ninguna designación como agente de retención/percepción IIBB. Con plantas en Luján, Ciudadela y Chascomús es la jurisdicción pendiente más relevante. ¿Existe designación? Constancia o número de agente.
2. **DGR Salta**: no vino designación como agente IIBB. El F600 que mandaste es la constancia de actividad **exenta por exportación** (CICSA como sujeto pasible) — otra cosa. ¿CICSA fue designada agente de retención/percepción en Salta?
3. **Río Negro**: no vino designación (planta en Allen). ¿Existe?

### B. Constancias a renovar o revalidar (las designaciones existen, el papel quedó viejo)

4. **ATM Mendoza**: la constancia venció el **09/04/2026**. Necesitamos la constancia renovada.
5. **API Santa Fe**: la constancia es de **2008**. Pedimos constancia/estado actual como agente. Recibimos la respuesta F1276 web — la revisamos en la próxima reunión juntos.
6. **AGIP CABA**: la designación es la Res. 1465-SHyF de **2001**. Confirmar que siguen en la nómina vigente de agentes AGIP (alcanza captura/constancia actual).
7. **ATER Entre Ríos**: la nómina adjunta es de **abril 2017**. Confirmar inclusión en la nómina vigente.
8. **IVA nacional**: la designación es la RG 608/99 sobre la nómina de la RG 18 (**1999**). Confirmar continuidad en el Anexo I de la RG 2854 vigente.
9. **San Luis**: la RG 16-DPIP-2007 los alcanza por encuadre (distribución de bebidas, art. 2 inc. b). ¿Figuran además en el Anexo I nominativo? ¿Cómo operan hoy ese régimen?

### C. Certificados propios por vencer — para que no LES retengan de más

10. **Santiago del Estero — cert. no ret./no perc. VENCE el 13/07/2026 (en días)**. ¿Está la renovación en curso?
11. **Catamarca — vence el 31/07/2026**. Ídem.
12. Recordatorio de vencimientos que siguen: **Chaco y Chubut 31/08/2026**, Corrientes 09/12/2026, Ganancias RG 830 31/03/2027, Salta F600 31/12/2026.

### D. SIRCAR

13. Constancia de **alta como agente en SIRCAR** y el listado de qué jurisdicciones presentan por SIRCAR vs. aplicativo local (Neuquén y Sgo. del Estero ya sabemos que van por SIRCAR).

### E. Municipal

14. Solo llegó la designación de la **Municipalidad de Córdoba**. Falta el relevamiento del resto de municipios con planta/depósito (Santa Fe capital —DReI—, Salta, Luján, Tres de Febrero, Chascomús, Allen): número de contribuyente de tasa y eventuales designaciones como agente.

### F. Del pedido original, sigue pendiente completo

15. **Reglas internas de Impuestos** (puntos 25-30 del pedido original): criterios de aprobación/bloqueo de proveedores, tratamiento del proveedor NO incluido en padrón por jurisdicción, política de certificados de exclusión de proveedores, mínimos 2026, monotributistas.
16. **Accesos a portales provinciales** (puntos 31-33, ver la aclaración de la actualización 2026-07-06): NO hace falta certificado ARCA de CICSA. Solo los archivos de padrón de agente de los portales (o acceso delegado para descargarlos); si algún día delegan servicios ARCA, se hace por Administrador de Relaciones, sin compartir claves. Todo intercambio sensible, por canal seguro definido de antemano.
17. **Padrones del mes** (puntos 34-36): los archivos de padrón vigentes que hoy usan para liquidar, y quién los descarga.
18. **Datos del piloto** (puntos 37-42): lista de 20-50 proveedores de prueba, 3-5 usuarios, volúmenes y criterios de éxito.
19. **ERP / maestro de proveedores** (punto 40): sistema y formato de exportación.
20. **Validador del catálogo** (punto 43): quién del equipo revisa lo que cargamos, con checkpoint quincenal durante el piloto.

## Prioridad sugerida

Si tenés que elegir por dónde empezar: **1 (ARBA)**, **10 (cert. Sgo. del Estero que vence en días)**, **4 (Mendoza renovada)** y **17 (padrones del mes)**. El resto puede venir en una segunda tanda.
