# Pedido de datos e información — CICSA/CCU (área Impuestos)

**Fecha:** 2026-07-03
**De:** Menter S.A.S. — plataforma de control fiscal de proveedores
**Para:** Responsable de Impuestos de CICSA / CCU Argentina
**Referencia:** Compañía Industrial Cervecera S.A. (CICSA), CUIT 30-50577985-8
**Objetivo:** Configurar la plataforma con la huella fiscal real de la compañía para la prueba piloto. Cada punto indica para qué se usa. Donde pedimos documentación, alcanza con copia escaneada/PDF; los originales quedan en la compañía.

> **Importante — seguridad:** ningún dato del bloque F (credenciales/certificados) debe enviarse por email plano. Antes de ese bloque definimos juntos un canal seguro. Todo lo demás puede ir por los canales habituales.

---

## A. Identificación societaria y fiscal

1. **Listado de sociedades del grupo que participan del piloto**: razón social, CUIT y rol (¿solo CICSA o también otras sociedades del grupo CCU Argentina?). *Uso: configurar el/los CUIT agente en la plataforma.*
2. **Constancia de inscripción ARCA vigente** de cada sociedad participante. *Uso: evidencia base del legajo del agente.*
3. **Constancia de inscripción en Convenio Multilateral** (número de inscripción CM y jurisdicciones dadas de alta — CM01/CM05 o constancia web). *Uso: confirmar la huella jurisdiccional que hoy tenemos estimada: Santa Fe, Salta, Buenos Aires, CABA, Córdoba, Mendoza, Río Negro, San Juan y Entre Ríos.*
4. **Última DDJJ CM05 (coeficientes unificados vigentes)** — solo el detalle de jurisdicciones y coeficientes, no los importes. *Uso: contexto de presencia territorial; no calculamos impuestos con esto.*
5. **Domicilios de plantas, depósitos y oficinas** con provincia y municipio (tenemos registradas: Santa Fe capital, Salta, Luján, Ciudadela, Chascomús y Allen — confirmar y completar). *Uso: relevamiento de tasas municipales y regímenes locales.*

## B. Designaciones como agente — Nacional (ARCA)

Para cada punto: **sí/no**, y si es sí, **copia de la resolución/constancia de designación o inscripción al régimen**.

6. ¿CICSA es **agente de retención de Ganancias (RG 830)**? Constancia de inscripción al régimen.
7. ¿Es **agente de retención de IVA** (RG 2854 u otro régimen aplicable)? ¿Por designación nominativa o por encuadre?
8. ¿Es **agente de percepción de IVA** (ventas a responsables inscriptos — RG 2408 u otro)? Constancia.
9. ¿Practica **retenciones de Seguridad Social (SUSS)** por servicios contratados (limpieza, seguridad/vigilancia, construcción u otros regímenes)? ¿Cuáles regímenes puntualmente?
10. ¿Practica **retenciones a beneficiarios del exterior** (Ganancias) por regalías/licencias de marcas o servicios del exterior? *Uso: lo tenemos como "probable" por las licencias internacionales; necesitamos confirmarlo.*
11. **¿Con qué sistema informan y certifican las retenciones/percepciones nacionales: SIRE, SICORE o ambos?** ¿Qué régimen va por cada sistema? *Uso: modelar los calendarios de vencimiento correctos.*
12. ¿La liquidación de retenciones la hace un **equipo interno o un estudio externo**? Si es externo: nombre y contacto del estudio.

## C. Designaciones como agente — Provinciales (IIBB)

Para **cada jurisdicción** de la lista, necesitamos: (a) si CICSA está designada como **agente de retención**, **de percepción**, ambos o ninguno; (b) **copia de la resolución/constancia de designación** con el número de agente; (c) **régimen aplicable** (general/especial); (d) si la DDJJ se presenta por **SIRCAR** o por aplicativo local.

13. **Santa Fe (API)** — sede y planta principal.
14. **Buenos Aires (ARBA)** — plantas Luján, Ciudadela y Chascomús.
15. **CABA (AGIP)**.
16. **Córdoba (Rentas Córdoba)**.
17. **Salta (DGR Salta)** — planta en la ciudad de Salta.
18. **Mendoza (ATM)**.
19. **Río Negro (Agencia de Recaudación)** — planta en Allen.
20. **San Juan y Entre Ríos** — figuran en la huella CM: ¿hay designación como agente en alguna de las dos?
21. ¿Hay **alguna otra jurisdicción** donde exista designación como agente (aunque no tengan planta)? *Uso: no queremos enterarnos por una intimación.*
22. ¿Están alcanzados por **SIRTAC** (retención sobre cobros con tarjetas/billeteras) en algún rol? *Uso: descartarlo o incorporarlo al mapa.*

## D. Ámbito municipal

23. **Listado de municipios** donde la compañía tributa tasa (TISH / DReI / equivalente), con número de contribuyente local.
24. ¿Algún municipio designó a CICSA como **agente de retención/percepción de tasas** (por ejemplo DReI Santa Fe)? Copia de la ordenanza/resolución si existe.

## E. Reglas internas del área Impuestos

25. **Criterios internos de aprobación/observación/bloqueo de proveedores** vigentes (matriz, instructivo o procedimiento interno, en el formato que tengan). *Uso: alinear el motor de decisión de la plataforma con el criterio de la compañía.*
26. **Tratamiento definido para el proveedor NO incluido en un padrón** por jurisdicción: ¿aplican alícuota general/residual/máxima o no retienen? ¿Con qué respaldo normativo? *Uso: punto crítico — la plataforma hoy alerta esta situación y necesita el criterio de la compañía para describirla bien.*
27. **Política de certificados de exclusión/no retención** (IVA, Ganancias, IIBB): ¿cómo los reciben, dónde los archivan y cómo controlan la vigencia?
28. **Mínimos no sujetos a retención** que están aplicando en 2026 (RG 830 y demás regímenes): ¿usan los valores actualizados de ARCA o una tabla propia?
29. **Tratamiento de proveedores monotributistas**: ¿controlan recurrencia/límites (RG 5329 y modificatorias)? ¿Con qué criterio los observan o retienen?
30. **Tratamiento de proveedores del exterior** (si compran a no residentes): criterio actual.

## F. Accesos y credenciales — SOLO por canal seguro

31. **Acceso ARCA para el web service de constancia de inscripción**: certificado digital + clave privada del servicio, o bien la decisión de delegar/autorizar la generación de un certificado específico para la plataforma. *Uso: pasar el sistema de modo demo a datos productivos en tiempo real. Definimos juntos la alternativa que Sistemas/Seguridad prefiera.*
32. **Portales provinciales para descarga de padrones** (ARBA, AGIP, API Santa Fe, Rentas Córdoba y demás jurisdicciones designadas): usuario de consulta/exportación **o**, si no quieren delegar acceso, el compromiso de envío mensual del archivo de padrón (ver bloque G).
33. **Contacto técnico de Sistemas/Seguridad informática** para coordinar el canal seguro y los accesos.

## G. Padrones y archivos mensuales

34. **Los archivos de padrón del período vigente que hoy usan para liquidar** (los mismos que descargan de ARBA, AGIP, API, etc.), tal cual los bajan, con fecha de descarga y período de vigencia. *Uso: cargar la plataforma con los padrones reales del mes y validar el cruce contra sus liquidaciones.*
35. **Quién descarga hoy cada padrón, de qué portal y con qué frecuencia** (persona/rol por jurisdicción). *Uso: mapear el circuito operativo actual y no duplicarlo.*
36. Si reciben **SIRCREB/SIRCAR** u otros archivos COMARB: ejemplo de archivo (puede ser de un período viejo).

## H. Datos operativos para el piloto

37. **Lista de 20 a 50 proveedores reales de prueba**: CUIT, razón social esperada, criticidad/volumen, y jurisdicción esperada si la conocen. *Uso: correr el piloto con casos reales y comparar contra lo que Impuestos ya sabe de cada uno.*
38. **3 a 5 usuarios piloto**: nombre, email, área y rol esperado (Compras, Cuentas a Pagar, Impuestos, Auditoría, Admin).
39. **Volumen mensual aproximado**: altas de proveedores nuevos por mes y cantidad de proveedores activos con pago mensual. *Uso: dimensionar la operación.*
40. **ERP / maestro de proveedores** que usan (SAP u otro) y formato en que pueden exportar el maestro (Excel/CSV). *Uso: carga masiva y futura integración.*
41. **Criterios de éxito del piloto** desde el punto de vista de Impuestos: ¿qué tendría que demostrar la plataforma para considerarla útil?
42. **Formato preferido de la evidencia**: Excel, PDF imprimible, link al legajo digital, o todos.

## I. Rol de validación normativa (acordado)

43. Confirmar **quién del equipo de Impuestos actuará como validador del catálogo normativo** de la plataforma durante el piloto (regímenes, vencimientos y criterios cargados), y con qué frecuencia puede revisar novedades (sugerimos un checkpoint quincenal durante el piloto).

---

**Priorización si no pueden juntar todo de una vez:** bloques **B y C** (designaciones) + punto **34** (padrones del mes) + punto **37** (proveedores de prueba) son los que destraban el piloto. El resto puede ir llegando en una segunda tanda.
