# Perfil fiscal del cliente — CIA INDUSTRIAL CERVECERA S.A. (CICSA)

**Fecha:** 2026-06-15
**Dato estructurado asociado:** `config/clientes_agentes.json`
**Propósito:** Documentar la huella fiscal del cliente piloto (grupo CCU) y el detalle de los regímenes de información, retención y percepción que la empresa debe **responder** y **generar** como agente.

> **Aclaración profesional.** Las designaciones concretas como agente por jurisdicción deben confirmarse con la documentación del propio cliente (constancias, claves fiscales, nóminas oficiales de agentes). Este documento parte del perfil público de la empresa y del criterio tributario general; no reemplaza el dictamen de un matriculado ni la norma vigente.

---

## 1. Identificación

| Campo | Dato |
|---|---|
| Razón social | CIA INDUSTRIAL CERVECERA S A |
| CUIT | 30-50577985-8 |
| Domicilio fiscal | Santa Fe, provincia de Santa Fe |
| Grupo económico | CCU Argentina (controlada por Compañía Cervecerías Unidas Argentina S.A.) |
| Actividad | Elaboración y comercialización de cerveza y maltas |
| Condición IVA | Responsable Inscripto |
| Ganancias | Inscripto |
| Ingresos Brutos | Convenio Multilateral |
| Marcas | Schneider, Imperial, Santa Fe, Salta, Palermo, Bieckert; licencias Heineken, Amstel, Budweiser |
| Huella territorial conocida | Plantas/depósitos en Santa Fe, Salta, Buenos Aires (Luján, Ciudadela, Chascomús), Río Negro (Allen), Mendoza (Las Heras); centros de distribución en Córdoba, Mendoza, San Juan, Rosario |

Esta huella nacional es la razón por la que la empresa tributa por Convenio Multilateral y es, casi con certeza, agente de recaudación de IIBB en varias jurisdicciones.

---

## 2. Aclaración clave: CICSA tiene dos roles fiscales distintos

Es fundamental no confundirlos, porque el sistema Menter hoy solo refleja el primero:

**Rol pasible (cómo figura HOY en el repositorio).** El CUIT de CICSA aparece como un renglón dentro de los padrones provinciales de IIBB cargados —ATER Entre Ríos, Córdoba y AGIP CABA— con alícuotas de retención y percepción de **0,10%**. Eso es la tasa que **otros agentes le aplican a CICSA** cuando le pagan o le venden. Es información sobre CICSA *como proveedor/cliente de terceros*, no sobre sus obligaciones como agente.

**Rol agente (lo que este documento agrega).** Por su tamaño y operación nacional, CICSA es además **agente de información, retención y percepción** en varios regímenes: tiene que *generar* retenciones/percepciones a sus propios proveedores y clientes, y *presentar* declaraciones e información. Eso es lo que el repositorio no tenía documentado y es lo que sigue.

---

## 3. Regímenes nacionales (ARCA)

### Información (debe responder/presentar)

**Libro IVA Digital** — régimen informativo mensual de compras y ventas. Obligatorio para Responsables Inscriptos; reemplazó al régimen CITI.

**SICOSS / Libro de Sueldos Digital** — declaración mensual de seguridad social como empleador. La planta de Santa Fe sola tiene del orden de 550 empleados, así que esta obligación es relevante.

**SIRE (Sistema Integral de Retenciones Electrónicas)** — sistema por el que el agente informa las retenciones/percepciones practicadas (seguridad social, IVA y Ganancias) y emite los certificados. **Importante (verificado a 2026):** SIRE y SICORE conviven; ARCA reordenó el cronograma de vencimientos para 2026 (RG 5652/2025). Hay que tratarlos como dos sistemas con calendarios propios.

### Retención (debe generar)

**Ganancias — RG 830** — agente de retención sobre pagos a proveedores, locadores, prestadores y profesionales. **Verificado a 2026:** los mínimos no sujetos a retención y los importes mínimos se actualizaron este año, por lo que las alícuotas/mínimos deben tomarse de tabla vigente, nunca fijos en código.

**IVA — regímenes de retención** — sujeto a designación de ARCA; alta probabilidad por perfil.

**Seguridad Social (SUSS)** — si contrata servicios alcanzados (limpieza, seguridad, construcción), actúa como agente de retención.

**Beneficiarios del exterior (Ganancias)** — probable por el pago de regalías/licencias de marcas internacionales (Heineken, Amstel, Budweiser); retención en la fuente sobre pagos al exterior.

### Percepción (debe generar)

**IVA — régimen de percepción** — como productor y distribuidor mayorista de bebidas, es un caso típico de agente de percepción de IVA a sus clientes (distribuidores, comercios).

---

## 4. Regímenes provinciales y Convenio Multilateral (IIBB)

**SIFERE — Convenio Multilateral.** Como contribuyente con operación en múltiples provincias, presenta la declaración de CM por SIFERE. Esto está confirmado por perfil.

**SIRCAR.** Sistema unificado de la Comisión Arbitral para que los agentes de retención/percepción de IIBB de las jurisdicciones adheridas presenten sus DDJJ en un solo lugar. Si CICSA es agente en jurisdicciones adheridas, opera por acá. **Verificado a 2026:** la Comisión Arbitral publicó los vencimientos 2026 de SIRCAR, SIRCREB, SIRTAC, SIRCUPA y SIFERE.

**SIRCREB.** Recaudación sobre acreditaciones bancarias. La empresa la **sufre** como contribuyente (le recaudan sobre sus cuentas), no la genera.

**Agente de recaudación provincial de IIBB.** Por huella, es muy probable que esté designada agente de retención y/o percepción de IIBB en, al menos: Santa Fe (API), Buenos Aires (ARBA), CABA (AGIP), Córdoba, Salta, Mendoza (ATM) y Río Negro. **Cada designación debe confirmarse contra la nómina oficial de agentes de cada provincia** — ese es el dato que falta pedirle al cliente.

---

## 5. Regímenes municipales

No hay un sistema unificado nacional. La estrategia correcta es relevar por huella: en los municipios donde CICSA tiene planta o depósito (ciudad de Santa Fe, ciudad de Salta, Luján, Ciudadela, Chascomús, Allen, Las Heras, etc.) tributa la **Tasa de Inspección, Seguridad e Higiene (TISH)** o el **Derecho de Registro e Inspección (DReI)** según la ordenanza local. Además, algunos municipios designan agentes de retención de DReI sobre pagos a proveedores; eso se confirma municipio por municipio.

---

## 6. Resumen del mapa (qué responde vs. qué genera)

| Nivel | Régimen / Sistema | Tipo | Rol de CICSA | Estado |
|---|---|---|---|---|
| Nacional | Libro IVA Digital | Información | Responde | Alta probabilidad |
| Nacional | SICOSS / Sueldos | Información | Responde | Alta probabilidad |
| Nacional | SIRE / SICORE | Información | Responde y genera | Confirmar |
| Nacional | Ganancias RG 830 | Retención | Genera | Alta probabilidad |
| Nacional | IVA retención | Retención | Genera | Confirmar designación |
| Nacional | IVA percepción | Percepción | Genera | Alta probabilidad |
| Nacional | SUSS | Retención | Genera | Confirmar |
| Nacional | Beneficiarios del exterior | Retención | Genera | Confirmar |
| Prov. unificado | SIFERE (CM) | Información | Responde | Confirmado por perfil |
| Prov. unificado | SIRCAR | Ret./Perc. | Genera | Confirmar designación |
| Prov. unificado | SIRCREB | Recaud. bancaria | Sufre | Alta probabilidad |
| Provincial | IIBB Santa Fe / ARBA / AGIP / Córdoba / Salta / Mendoza / Río Negro | Ret./Perc. | Genera | Confirmar designación |
| Municipal | TISH / DReI | Tasa / posible retención | Responde y posible genera | Relevar por huella |

---

## 7. Qué falta pedirle a CICSA para cerrar el detalle

Para pasar de "muy probable por perfil" a "confirmado", el cliente debe aportar:

La **constancia de inscripción de ARCA** del CUIT (confirma IVA, Ganancias, actividades y domicilios). El **listado de jurisdicciones donde está designada agente de retención/percepción de IIBB**, con número de inscripción de agente en cada una. Las **claves fiscales / accesos delegados** a SIRE, SICORE, SIRCAR y a los portales provinciales (para el circuito de evidencia que ya prevé el módulo de accesos). El **detalle de sociedades del grupo** que operan junto a CICSA (CCU Argentina S.A., Gestión Cervecera SAS y otras que aparecen en los mismos padrones), por si el alcance del piloto incluye más de un CUIT. Y los **municipios** donde tiene establecimientos, para el relevamiento de tasas locales.

---

## 8. Cómo se conecta esto con el sistema

El dato quedó cargado en `config/clientes_agentes.json` con un estado de confirmación por régimen. El siguiente paso natural (alineado con el plan de mejoras priorizado) es que el sistema **lea ese archivo** para mostrar, en la pantalla de configuración o en el dashboard del piloto, el mapa de regímenes del cliente y su estado, y que el módulo de accesos fiscales (`accesos_fiscales.py`) se apoye en él para saber qué accesos hay que gestionar. Hoy el archivo es un dato estructurado listo para usar; todavía no hay código que lo consuma.

---

## Fuentes

- CIA INDUSTRIAL CERVECERA S A (CUIT 30-50577985-8) — Cuit Online: https://www.cuitonline.com/detalle/30505779858/cia-industrial-cervecera-s-a.html
- Compañía Industrial Cervecería S.A. (CCU Argentina) — Birrapedia: https://birrapedia.com/en/compania-industrial-cerveceria-sa-ccu-argentina/e-578f547b1603da0b497b8770
- Nuestras Plantas — CCU Argentina: https://www.ccu.com.ar/somos-ccu/como-lo-hacemos/nuestras-plantas/
- SIRE — Sistema Integral de Retenciones Electrónicas (ARCA): https://www.afip.gob.ar/sire/
- Comisión Arbitral del Convenio Multilateral (COMARB): https://www.ca.gob.ar/
- RG 830 Ganancias — conceptos alcanzados (ARCA): https://www.afip.gob.ar/gananciasYBienes/ganancias/retenciones/rg830/conceptos-alcanzados.asp
