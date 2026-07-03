# Plan de mejoras priorizado — Menter Fiscal

**Fecha de corte:** 2026-06-15
**Autor del análisis:** Revisión técnico-fiscal (Cowork / Claude) a pedido de Menter S.A.S.
**Alcance:** Backlog accionable y priorizado sobre cuatro ejes: cumplimiento fiscal, formato y formalidades del legajo, verificación normativa 2026 y arquitectura enterprise.

> **Aclaración profesional.** Este documento es asistencia técnica y organizativa. No reemplaza el dictamen de un contador/tributarista matriculado ni la liquidación definitiva de retenciones, percepciones e información. Las referencias normativas deben validarse con la norma vigente al momento de implementar cada cambio.

---

## 1. Cómo leer las prioridades

Cada mejora tiene una prioridad operativa, en el mismo lenguaje que ya usa el proyecto en sus catálogos de fuentes:

- **P0 — Crítico:** sin esto, el sistema puede inducir una decisión fiscal equivocada o no es apto para producción real. Se hace primero.
- **P1 — Alto:** necesario para un piloto serio en una empresa mediana/grande.
- **P2 — Medio:** mejora sustancial de cobertura o robustez; se planifica después del piloto.
- **P3 — Evolutivo:** producto a mediano plazo (SaaS, multiempresa, integraciones amplias).

Cada item incluye **qué se toca** (archivo o módulo concreto) para que puedas avanzarlo paso a paso en modo vibe coding.

---

## 2. Punto de partida: qué está bien y no hay que romper

Antes del backlog, conviene fijar lo que el proyecto ya hace bien, porque son decisiones de diseño que hay que **preservar**, no rehacer:

La arquitectura separa correctamente *dato* (respuesta de ARCA, padrón, fuente online), *regla* (criterio tributario) y *decisión* (estado del proveedor). Clasifica regímenes por nivel —nacional, provincial unificado/COMARB, provincial y municipal— en lugar de tratarlos como portales sueltos. El criterio de que **una fuente no consultable no se marca como "no inscripto"** sino como pendiente/asistida es la decisión de riesgo más importante del sistema y está bien tomada: evita falsos negativos que llevarían a no retener cuando se debe. La verificación contra base APOC, el tratamiento del monotributo como observación, el legajo con hash SHA256 y la disciplina documental (los `AGENTS.md` y `scripts/check_dox.py`) son fortalezas reales que ningún cambio del backlog debe debilitar.

---

## 3. Hallazgos de verificación normativa 2026

Verifiqué contra fuentes oficiales y profesionales el estado actual de los sistemas y regímenes que el proyecto modela. Conclusiones que impactan el diseño:

**SIRE y SICORE conviven en 2026.** El SIRE (Sistema Integral de Retenciones Electrónicas) es el sistema por el que los agentes informan retenciones/percepciones de seguridad social, IVA y Ganancias y emiten los certificados. SICORE (RG 2233) sigue vigente para determinados regímenes. ARCA modificó el cronograma de vencimientos para 2026 (RG 5652/2025), concentrando obligaciones en menos días. **Implicancia:** el catálogo de regímenes debe modelar SIRE y SICORE como dos sistemas de información coexistentes, con sus propios calendarios de vencimiento, y no como uno solo.

**Los mínimos y escalas de RG 830 (Ganancias) se actualizaron para 2026.** Cambiaron los montos mínimos no sujetos a retención y los importes mínimos de retención (por ejemplo, mínimos de bienes/servicios y de honorarios profesionales subieron de forma significativa por inflación). **Implicancia:** los importes NO deben quedar nunca "hard-codeados" en el código. Tienen que vivir en configuración versionada con fecha de vigencia, para poder actualizarlos sin tocar la lógica.

**Los sistemas COMARB están activos con calendario 2026 publicado.** La Comisión Arbitral publicó (RG 20 a 24/2025, diciembre 2025) los vencimientos 2026 de SIRCAR, SIRCREB, SIRTAC, SIRCUPA y SIFERE. **Implicancia:** el catálogo de regímenes provinciales unificados está bien identificado; lo que falta es conectarlo con vencimientos y padrones reales.

**ARCA es la denominación vigente (ex AFIP).** El proyecto ya usa "AFIP/ARCA" de forma consistente, lo cual es correcto.

---

## 4. Eje A — Cumplimiento fiscal

| # | Prioridad | Mejora | Qué se toca |
|---|---|---|---|
| A1 | **P0** | **Parametrizar mínimos, escalas y alícuotas con vigencia.** Hoy la matriz consolida señales pero no calcula. El primer paso no es calcular todo, sino sacar cualquier importe del código y llevarlo a un catálogo versionado (`config/`) con `vigencia_desde` / `vigencia_hasta`. Esto habilita actualizar RG 830 2026 sin reprogramar. | nuevo `config/reglas_tributarias.json` + `matriz_tributaria.py` |
| A2 | **P0** | **Bloquear aprobación en modo DEMO/fallback de ARCA.** El legajo de muestra revisado se generó en modo DEMO (Banco Nación, "AFIP live: 0"). El motor ya lo manda a REVISIÓN MANUAL, pero hay que asegurar que **ningún** estado APROBABLE pueda salir con datos demo, y dejarlo explícito en el legajo. | `riesgo_fiscal.py`, `legajos.py` |
| A3 | **P1** | **Modelar SIRE y SICORE como sistemas separados** con sus calendarios 2026. Hoy aparecen agrupados. | `config/regimenes_catalogo.json` |
| A4 | **P1** | **Completar el catálogo de regímenes.** 12 de 21 entradas están en estado `pendiente_catalogado`. Priorizar las que apliquen a la huella real del cliente piloto (ver sección 8). | `config/regimenes_catalogo.json`, `docs/AUDITORIA_REGIMENES_ARGENTINA.md` |
| A5 | **P1** | **Manejo de certificados de exclusión/no retención con vigencia** (Ganancias e IVA). Hoy la matriz solo recomienda "controlar certificado"; no los carga ni verifica vencimiento. Es una fuente frecuente de retenciones mal practicadas. | nuevo módulo `certificados.py` + matriz |
| A6 | **P2** | **Incorporar Seguridad Social (SUSS).** No está cubierto y es parte del universo SIRE. | catálogo + matriz |
| A7 | **P2** | **Convenio Multilateral: distinguir jurisdicciones declaradas de coeficientes.** Las jurisdicciones que informa la constancia ARCA no son los coeficientes de atribución; conviene dejarlo explícito para no inducir error. | `regimenes_aplicables.py`, `matriz_tributaria.py` |
| A8 | **P2** | **Régimen de retención a monotributistas por exceso de límites.** Hoy monotributo = OBSERVADO genérico; afinar el criterio. | `riesgo_fiscal.py` |

---

## 5. Eje B — Formato y formalidades del legajo y la evidencia

Esta es la parte que una empresa grande mira con lupa, porque es lo que se presenta ante auditoría interna, externa o una inspección.

| # | Prioridad | Mejora | Qué se toca |
|---|---|---|---|
| B1 | **P0** | **Alinear el reporte Excel con lo documentado.** El README describe una hoja "Matriz tributaria" en el Excel, pero el archivo de salida real revisado tiene Resumen, AFIP-ARCA, Padrones IIBB, Fuentes online y Trazabilidad — falta la hoja Matriz. Hay que cerrar esa inconsistencia (agregar la hoja o corregir la doc). | `excel.py`, `README.md` |
| B2 | **P1** | **Versión de reglas aplicadas dentro del legajo.** Para que una decisión sea reconstruible años después, el legajo debe registrar qué versión del catálogo de reglas/alícuotas se usó, no solo los datos consultados. | `legajos.py`, `excel.py` |
| B3 | **P1** | **Sellado temporal e inmutabilidad del legajo.** Hoy el legajo tiene hash SHA256 e ID; falta garantizar que una vez cerrado no se modifica (campo de estado "cerrado" + hash del JSON completo). | `legajos.py` |
| B4 | **P1** | **Identidad del operador y de la decisión.** El legajo debería registrar qué usuario disparó la validación y quién resolvió una observación (depende de B en eje C: roles). | `legajos.py` |
| B5 | **P2** | **Exportación PDF firmable del legajo**, además del Excel/JSON, para circuitos formales de aprobación. | nuevo `pdf_legajo.py` |
| B6 | **P2** | **Diccionario de datos del legajo** (qué significa cada campo y de qué fuente proviene), como anexo formal para auditoría. | `docs/` |

---

## 6. Eje C — Arquitectura enterprise

El propio proyecto ya tiene esto bien diagnosticado en `docs/ARQUITECTURA_ENTERPRISE.md` y `ROADMAP_ENTERPRISE.md`. Lo prioricé:

| # | Prioridad | Mejora | Qué se toca |
|---|---|---|---|
| C1 | **P0** | **Gestión segura de secretos y certificados fiscales.** Hoy las credenciales ARCA van por variables de entorno y hay `.pem` en el árbol. Para producción se necesita un secret manager y que ningún certificado/clave fiscal viva en el repositorio. | despliegue + `.gitignore` + `afip_arca.py` |
| C2 | **P0** | **Autenticación real con roles.** Hoy hay Basic Auth única. Una empresa necesita usuarios y roles (admin, impuestos, compras, cuentas a pagar, auditoría) con registro de acciones. | `main.py` + capa de auth |
| C3 | **P1** | **Persistencia en base de datos.** Migrar legajos, proveedores y estados de archivos locales a PostgreSQL/Supabase (ya hay migraciones iniciales en `supabase/`). | `supabase/`, módulos de persistencia |
| C4 | **P1** | **Object storage para evidencias** (Excel, PDFs, padrones originales, capturas) separado de la base. | despliegue |
| C5 | **P1** | **Auditoría de acciones (log inmutable):** quién hizo qué y cuándo. Requisito de compliance. | nueva tabla + middleware |
| C6 | **P2** | **Cola de trabajos** para lotes grandes y fuentes lentas (ya hay base con `process_padron_job.py` y Cloud Run). | scripts + worker |
| C7 | **P2** | **Multi-tenant (separación por empresa)** con configuración fiscal por cliente. | modelo de datos |
| C8 | **P3** | **Integración con ERP y maestro de proveedores** (SAP, Tango, Finnegans, etc.) y orquestación con n8n. | integraciones |

---

## 7. Eje D — Verificación normativa continua

El riesgo más sutil de un sistema fiscal no es el bug de código: es que la norma cambie y el sistema siga aplicando la vieja. Mejoras para que eso no pase:

| # | Prioridad | Mejora | Qué se toca |
|---|---|---|---|
| D1 | **P1** | **Fecha de última verificación normativa por régimen.** Cada entrada del catálogo debería decir "norma verificada al AAAA-MM-DD" y la fuente oficial. | `config/regimenes_catalogo.json` |
| D2 | **P1** | **Calendario de vencimientos 2026** (SIRE/SICORE/COMARB) integrado al monitor de fuentes que ya existe (`/fuentes`). | `fuentes_catalogo.json`, monitor |
| D3 | **P2** | **Alerta de desactualización normativa:** si un régimen lleva X meses sin reverificar, el monitor lo marca. Reusa la lógica de vigencia de padrones que ya está implementada. | monitor de fuentes |
| D4 | **P2** | **Revisión profesional periódica** documentada: un tributarista valida el catálogo cada cierre de cuatrimestre y firma. | proceso + `docs/` |

---

## 8. Qué necesito del cliente para cerrar la opinión de fondo

Para pasar de "está bien diseñado" a "cumple para esta empresa según la norma vigente", hacen falta estos insumos (sin ellos, las recomendaciones fiscales son sobre el motor en abstracto, no sobre el caso real):

La **huella fiscal del cliente piloto** (se menciona CCU): en qué jurisdicciones fue designado agente de retención/percepción, dónde tiene domicilios, plantas y depósitos, y dónde concentra proveedores. Esto define qué regímenes aplican de verdad. La **especificación de reglas de Impuestos**: alícuotas, mínimos y criterios que la empresa quiere aplicar. Un **legajo real y padrones reales de muestra** para evaluar suficiencia probatoria. Y la **confirmación de credenciales productivas de ARCA** (hoy el sistema corre en modo demo).

---

## 9. Secuencia sugerida para vibe coding

Si tuvieras que avanzarlo paso a paso, este es el orden que recomiendo, de menor a mayor complejidad y respetando dependencias:

1. **B1** (alinear Excel con la doc) — cambio chico, cierra una inconsistencia visible.
2. **A1** (sacar importes del código a `config/reglas_tributarias.json` con vigencia) — habilita todo lo demás del eje fiscal.
3. **A2 + B2 + B3** (blindar modo demo y dejar versión de reglas + sello en el legajo) — sube la calidad de la evidencia.
4. **C1 + C2** (secretos y auth con roles) — requisito para cualquier piloto real.
5. **A3, A4, D1, D2** (catálogo de regímenes y verificación normativa) — cobertura fiscal.
6. **C3 en adelante** (persistencia, storage, auditoría) — camino enterprise.

Cada paso es testeable de forma aislada, lo cual encaja con la disciplina de tests que el proyecto ya tiene.

---

## Estado de ejecución (actualizado 2026-07-03)

Auditoría técnico-fiscal de julio 2026 (Sprint 0 "Blindaje P0 fiscal") ejecutó correcciones que este plan no había detectado, además de ítems propios:

- **Hecho antes de julio:** B1 (hoja "Matriz tributaria" en el Excel).
- **Sprint 0 (2026-07-03):** APOC pasa a "NO VERIFICADO" con derivación a revisión manual (relacionado a A2: ningún APROBABLE puede salir sin verificación APOC); fix del dígito verificador (DV calculado 10 ya no se acepta como 9); los padrones dejaron de afirmar "no aplica retención/percepción" para CUITs no incluidos; la vigencia del padrón ahora impacta consulta, decisión y matriz; CI en GitHub Actions con la suite completa.
- **Pendiente:** A1 (reglas tributarias parametrizadas con vigencia), A3-A8, B2-B6, C1-C8, D1-D4.

## Fuentes (verificación normativa 2026)

- SIRE — Sistema Integral de Retenciones Electrónicas (ARCA): https://www.afip.gob.ar/sire/
- Normativa SIRE (ARCA): https://www.afip.gob.ar/sire/ayuda/normativa.asp
- Adecuación de vencimientos SIRE/SICORE — CPCE Córdoba: https://web.cpcecba.org.ar/arca-adecua-vencimientos-de-las-retenciones-de-sire-y-sicore/
- RG 830 Ganancias — conceptos alcanzados (ARCA): https://www.afip.gob.ar/gananciasYBienes/ganancias/retenciones/rg830/conceptos-alcanzados.asp
- Mínimos no sujetos a retención 2026 — análisis profesional: https://www.iprofesional.com/impuestos/447327-ganancias-e-iva-montos-minimos-absurdos-arca-exige-retenciones-2026
- Comisión Arbitral del Convenio Multilateral (COMARB): https://www.ca.gob.ar/
- SIRCAR (COMARB): https://www.ca.gob.ar/sistemas/sircar
- SIRCREB (COMARB): https://www.ca.gob.ar/resultados/sistemas/sircreb
