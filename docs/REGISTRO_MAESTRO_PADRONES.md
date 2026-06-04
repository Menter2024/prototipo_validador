# Registro maestro de padrones fiscales

Actualizado: 2026-06-04.

Este archivo es el inventario operativo que debe mantenerse para importar padrones reales al sistema. Su objetivo es que cada fuente tenga registrado: dónde se obtiene el padrón, dónde se consulta el formato/instructivo, qué acceso requiere, qué layout interno lo traduce al modelo canónico y qué evidencia debe conservarse.

## Alcance de cobertura

- Nacional: ARCA y servicios/regímenes nacionales relevantes.
- Convenio Multilateral: COMARB / Padrones y regímenes SIFERE, SIRCREB, SIRCUPA, SIRCIP, SIRCAR y SIRTAC.
- Provincial/CABA: fuente inicial para las 24 jurisdicciones argentinas: Buenos Aires, CABA y 22 provincias.
- Municipal: no se puede declarar exhaustivo sin la huella real del cliente; se registra un punto de partida nacional y la regla para incorporar municipios según actividad/sucursales/depósitos.

## Reglas de mantenimiento

1. Cada fuente debe existir en `config/fuentes_catalogo.json` y aparecer en este registro.
2. Cada descarga/importación real debe conservar archivo original, hash SHA-256, fecha/hora, usuario/origen, período/vigencia, URL usada y resultado de validación.
3. Si el portal exige credenciales, CAPTCHA o interacción humana, no se debe automatizar el bypass: se usa cola asistida o integración oficial habilitada.
4. Si cambia el formato, se crea un nuevo `layout_id` en `config/padron_layouts.json`; nunca se pisa silenciosamente el layout anterior.
5. Para demostrar funcionamiento, cada fuente priorizada debe tener lote de prueba con CUITs reales trazables y casos que aparezcan en múltiples padrones.
6. Las URLs deben revisarse por sprint antes de una demo/piloto y luego con frecuencia mensual o ante cambios normativos.

## Campos canónicos esperados

El importador debe traducir cada formato externo hacia estos campos mínimos: `cuit`, `alicuota_retencion`, `alicuota_percepcion`, `vigencia_desde`, `vigencia_hasta`, `regimen`, `jurisdiccion`, `tipo_padron`, `fuente_id`, `layout_id`.

## Registro de fuentes

| ID | Jurisdicción | Organismo | Padrón / alcance | Obtención oficial | Formato / instructivo | Acceso | Frecuencia | Layout interno | Estado | Instrucción operativa |
|---|---|---|---|---|---|---|---|---|---|---|
| `arba_iibb` | Buenos Aires | ARBA | Ingresos Brutos · retención/percepción por sujeto | [obtener](https://web.arba.gov.ar/regimen-de-recaudacion-por-sujeto) | [formato/instructivo](https://web.arba.gov.ar/regimen-de-recaudacion-por-sujeto) | requiere_credenciales | mensual | `pendiente_layout_especifico` + genérico | catalogado | Verificar fuente oficial y conservar evidencia de acceso/descarga. |
| `agip_caba_iibb` | CABA | AGIP | Ingresos Brutos · retención/percepción | [obtener](https://imagenes.agip.gob.ar/agentes/agentes-de-recaudacion-e-informacion) | [formato/instructivo](https://imagenes.agip.gob.ar/agentes/agentes-de-recaudacion-e-informacion) | pagina_publica_links | mensual | `agip_caba_regimenes_generales_v1` | catalogado | Verificar fuente oficial y conservar evidencia de acceso/descarga. |
| `comarb_sircip` | Convenio Multilateral | Comisión Arbitral | Sistema unificado de percepciones IIBB y padrón de contribuyentes alcanzados | [obtener](https://www.ca.gob.ar/sistemas/sircip) | [formato/instructivo](https://www.ca.gob.ar/sistemas/sircip) | portal_credenciales | mensual | no aplica / consulta asistida | catalogado_no_integrado | CUIT agente/contribuyente habilitado |
| `comarb_sircreb` | Convenio Multilateral | Comisión Arbitral | Recaudación bancaria IIBB sobre acreditaciones | [obtener](https://www.ca.gob.ar/index.php/sistemas/sircreb) | [formato/instructivo](https://www.ca.gob.ar/index.php/sistemas/sircreb) | portal_credenciales | mensual | no aplica / consulta asistida | catalogado_no_integrado | CUIT agente/contribuyente habilitado |
| `comarb_sircupa` | Convenio Multilateral | Comisión Arbitral | Recaudación IIBB sobre acreditaciones en cuentas de pago/PSP | [obtener](https://www.ca.gob.ar/sistemas/sircupa) | [formato/instructivo](https://www.ca.gob.ar/sistemas/sircupa) | portal_credenciales | mensual | no aplica / consulta asistida | catalogado_no_integrado | CUIT agente/contribuyente habilitado |
| `ater_entrerios_iibb` | Entre Ríos | ATER | Ingresos Brutos · retención/percepción | [obtener](https://www.ater.gov.ar/ater2/NominasAgentes.asp) | [formato/instructivo](https://www.ater.gov.ar/ater2/NominasAgentes.asp) | monitoreo_publicacion | mensual | `pendiente_layout_especifico` + genérico | catalogado | Verificar fuente oficial y conservar evidencia de acceso/descarga. |
| `arca_apoc` | Nacional | ARCA | Señal de riesgo sobre usinas/facturación apócrifa y controles preventivos de proveedor | [obtener](https://www.arca.gob.ar/facturacion/default.asp) | [formato/instructivo](https://www.arca.gob.ar/facturacion/default.asp) | requiere_navegador | alta_y_revalidacion | no aplica / consulta asistida | pendiente_relevar_endpoint | CUIT proveedor |
| `arca_constancia` | Nacional | ARCA | Inscripción, estado fiscal, impuestos nacionales e inscripción IIBB/Convenio Multilateral declarada en constancia | [obtener](https://www.afip.gob.ar/ws/) | [formato/instructivo](https://www.afip.gob.ar/ws/) | publico | online_en_cada_alta | no aplica / consulta asistida | catalogado | Verificar fuente oficial y conservar evidencia de acceso/descarga. |
| `arca_sire` | Nacional | ARCA | Sistema Integral de Retenciones Electrónicas; presentación/certificación de retenciones y percepciones nacionales | [obtener](https://arca.gob.ar/sire/) | [formato/instructivo](https://arca.gob.ar/sire/) | portal_credenciales | por_operacion_y_vencimiento | no aplica / consulta asistida | catalogado_no_integrado | CUIT agente con clave fiscal |
| `santafe_iibb` | Santa Fe | API Santa Fe | Ingresos Brutos · retención/percepción | [obtener](https://www.santafe.gob.ar/index.php/web/content/view/full/221362/(subtema)/102284) | [formato/instructivo](https://www.santafe.gob.ar/index.php/web/content/view/full/221362/(subtema)/102284) | portal_credenciales | mensual | `pendiente_layout_especifico` + genérico | catalogado | Verificar fuente oficial y conservar evidencia de acceso/descarga. |
| `chubut_iibb_agentes` | Chubut | ARECH Chubut | Ingresos Brutos · inscripción, agentes, retención/percepción y/o certificados según portal jurisdiccional | [obtener](https://www.dgrchubut.gov.ar/agentes-de-retencion-y-percepcion/) | [formato/instructivo](https://www.dgrchubut.gov.ar/agentes-de-retencion-y-percepcion/) | pendiente_relevamiento | alta_y_revalidacion | no aplica / consulta asistida | pendiente_relevamiento_p2 | Confirmar servicio oficial vigente |
| `comarb_sifere_padron` | Convenio Multilateral | Comisión Arbitral | Constancia e información de inscripción Convenio Multilateral | [obtener](https://www.ca.gob.ar/sistemas/padron-web-padron-federal) | [formato/instructivo](https://www.ca.gob.ar/sistemas/padron-web-padron-federal) | portal_credenciales | mensual | no aplica / consulta asistida | catalogado_no_integrado | CUIT agente/contribuyente habilitado |
| `comarb_sircar` | Convenio Multilateral | Comisión Arbitral | Retenciones/percepciones IIBB de agentes en jurisdicciones adheridas | [obtener](https://www.ca.gob.ar/sistemas/sircar) | [formato/instructivo](https://www.ca.gob.ar/sistemas/sircar) | portal_credenciales | mensual | no aplica / consulta asistida | catalogado_no_integrado | CUIT agente/contribuyente habilitado |
| `comarb_sirtac` | Convenio Multilateral | Comisión Arbitral | Recaudación IIBB sobre tarjetas/medios de pago | [obtener](https://www.ca.gob.ar/sistemas/sirtac) | [formato/instructivo](https://www.ca.gob.ar/sistemas/sirtac) | portal_credenciales | mensual | no aplica / consulta asistida | catalogado_no_integrado | CUIT agente/contribuyente habilitado |
| `corrientes_iibb_online` | Corrientes | DGR Corrientes | Inscripción IIBB / padrones bajo acceso | [obtener](https://www.dgrcorrientes.gov.ar/rentascorrientes/consultarContenido.do?categoria=199) | [formato/instructivo](https://www.dgrcorrientes.gov.ar/rentascorrientes/consultarContenido.do?categoria=199) | portal_credenciales | segun_exportacion_cliente | no aplica / consulta asistida | catalogado | Verificar fuente oficial y conservar evidencia de acceso/descarga. |
| `cordoba_iibb` | Córdoba | Rentas Córdoba | Ingresos Brutos · retención/percepción | [obtener](https://www.rentascordoba.gob.ar/cms/ms-agentes/) | [formato/instructivo](https://www.rentascordoba.gob.ar/cms/ms-agentes/) | pagina_publica_links | mensual | `pendiente_layout_especifico` + genérico | catalogado | Verificar fuente oficial y conservar evidencia de acceso/descarga. |
| `jujuy_iibb` | Jujuy | DPR Jujuy | Ingresos Brutos · retención/percepción | [obtener](https://rentasjujuy.gob.ar/agentes-ingresos-brutos/) | [formato/instructivo](https://rentasjujuy.gob.ar/agentes-ingresos-brutos/) | pagina_publica_links | mensual | `pendiente_layout_especifico` + genérico | catalogado | Verificar fuente oficial y conservar evidencia de acceso/descarga. |
| `mendoza_iibb` | Mendoza | ATM Mendoza | Ingresos Brutos · retención/percepción | [obtener](https://www.atm.mendoza.gov.ar/) | [formato/instructivo](https://www.atm.mendoza.gov.ar/) | portal_credenciales | mensual | `pendiente_layout_especifico` + genérico | catalogado | Verificar fuente oficial y conservar evidencia de acceso/descarga. |
| `misiones_iibb_online` | Misiones | ATM Misiones | Inscripción IIBB por CUIT | [obtener](https://sinclavefiscal.atm.misiones.gob.ar/sc/ingresos-brutos/constancia-inscripcion) | [formato/instructivo](https://sinclavefiscal.atm.misiones.gob.ar/sc/ingresos-brutos/constancia-inscripcion) | requiere_navegador | alta_y_revalidacion | no aplica / consulta asistida | catalogado | Verificar fuente oficial y conservar evidencia de acceso/descarga. |
| `rionegro_iibb_online` | Río Negro | Agencia de Recaudación Río Negro | Inscripción IIBB por CUIT | [obtener](https://agenciaws.rionegro.gov.ar/InscripcionesContribuyente/) | [formato/instructivo](https://agenciaws.rionegro.gov.ar/InscripcionesContribuyente/) | requiere_captcha | alta_y_revalidacion | no aplica / consulta asistida | catalogado | Verificar fuente oficial y conservar evidencia de acceso/descarga. |
| `tucuman_iibb` | Tucumán | DGR Tucumán | Ingresos Brutos · retención/percepción | [obtener](https://www.rentastucuman.gob.ar/) | [formato/instructivo](https://www.rentastucuman.gob.ar/) | pagina_publica_links | mensual | `pendiente_layout_especifico` + genérico | catalogado | Verificar fuente oficial y conservar evidencia de acceso/descarga. |
| `catamarca_iibb_online` | Catamarca | ARCAT | Ingresos Brutos · inscripción, agentes, retención/percepción y/o certificados según portal jurisdiccional | [obtener](https://arcat.gob.ar/) | [formato/instructivo](https://arcat.gob.ar/) | pendiente_relevamiento | alta_y_revalidacion | no aplica / consulta asistida | pendiente_relevamiento_p2 | Confirmar servicio oficial vigente |
| `chaco_iibb_online` | Chaco | ATP Chaco | Ingresos Brutos · inscripción, agentes, retención/percepción y/o certificados según portal jurisdiccional | [obtener](https://atp.chaco.gob.ar/) | [formato/instructivo](https://atp.chaco.gob.ar/) | pendiente_relevamiento | alta_y_revalidacion | no aplica / consulta asistida | pendiente_relevamiento_p2 | Confirmar servicio oficial vigente |
| `formosa_iibb` | Formosa | DGR Formosa | Ingresos Brutos · retención/percepción | [obtener](https://www.formosa.gob.ar/tramite/120/inscripcion_como_agente_de_percepcion_del_impuesto_sobre_los_ingresos_brutos) | [formato/instructivo](https://www.formosa.gob.ar/tramite/120/inscripcion_como_agente_de_percepcion_del_impuesto_sobre_los_ingresos_brutos) | archivo_cliente | mensual | `pendiente_layout_especifico` + genérico | catalogado | Verificar fuente oficial y conservar evidencia de acceso/descarga. |
| `lapampa_iibb_online` | La Pampa | DGR La Pampa | Ingresos Brutos · inscripción, agentes, retención/percepción y/o certificados según portal jurisdiccional | [obtener](https://www.dgr.lapampa.gob.ar/) | [formato/instructivo](https://www.dgr.lapampa.gob.ar/) | pendiente_relevamiento | alta_y_revalidacion | no aplica / consulta asistida | pendiente_relevamiento_p2 | Confirmar servicio oficial vigente |
| `larioja_iibb_online` | La Rioja | DGIP La Rioja | Ingresos Brutos · inscripción, agentes, retención/percepción y/o certificados según portal jurisdiccional | [obtener](https://dgip.larioja.gob.ar/) | [formato/instructivo](https://dgip.larioja.gob.ar/) | pendiente_relevamiento | alta_y_revalidacion | no aplica / consulta asistida | pendiente_relevamiento_p2 | Confirmar servicio oficial vigente |
| `salta_iibb_online` | Salta | DGR Salta | Ingresos Brutos · inscripción, agentes, retención/percepción y/o certificados según portal jurisdiccional | [obtener](https://www.dgrsalta.gov.ar/) | [formato/instructivo](https://www.dgrsalta.gov.ar/) | pendiente_relevamiento | alta_y_revalidacion | no aplica / consulta asistida | pendiente_relevamiento_p2 | Confirmar servicio oficial vigente |
| `sanjuan_iibb_online` | San Juan | DGR San Juan | Ingresos Brutos · inscripción, agentes, retención/percepción y/o certificados según portal jurisdiccional | [obtener](https://rentas.dgrsj.gob.ar/) | [formato/instructivo](https://rentas.dgrsj.gob.ar/) | pendiente_relevamiento | alta_y_revalidacion | no aplica / consulta asistida | pendiente_relevamiento_p2 | Confirmar servicio oficial vigente |
| `sanluis_iibb_online` | San Luis | DPIP San Luis | Ingresos Brutos · inscripción, agentes, retención/percepción y/o certificados según portal jurisdiccional | [obtener](https://dpip.sanluis.gov.ar/) | [formato/instructivo](https://dpip.sanluis.gov.ar/) | pendiente_relevamiento | alta_y_revalidacion | no aplica / consulta asistida | pendiente_relevamiento_p2 | Confirmar servicio oficial vigente |
| `municipal_padrones_huella_cliente` | Municipal | Municipios/Comunas | TISH, DReI, Comercio e Industria, tasas locales y regímenes de retención/percepción/información municipales | [obtener](https://www.argentina.gob.ar/municipios) | [formato/instructivo](https://www.argentina.gob.ar/municipios) | cola_asistida | segun_huella_cliente | no aplica / consulta asistida | marco_general | Mapa de sucursales/operaciones del cliente |
| `neuquen_iibb_online` | Neuquén | Rentas Neuquén | Inscripción IIBB por CUIT | [obtener](https://rentasneuquenweb.gob.ar/nqn/SCF/cons_inscripcion.php) | [formato/instructivo](https://rentasneuquenweb.gob.ar/nqn/SCF/cons_inscripcion.php) | consulta_online_cuit | alta_y_revalidacion | no aplica / consulta asistida | catalogado | Verificar fuente oficial y conservar evidencia de acceso/descarga. |
| `santacruz_iibb_online` | Santa Cruz | ASIP Santa Cruz | Ingresos Brutos · inscripción, agentes, retención/percepción y/o certificados según portal jurisdiccional | [obtener](https://asip.gob.ar/) | [formato/instructivo](https://asip.gob.ar/) | pendiente_relevamiento | alta_y_revalidacion | no aplica / consulta asistida | pendiente_relevamiento_p3 | Confirmar servicio oficial vigente |
| `santiago_iibb_online` | Santiago del Estero | DGR Santiago del Estero | Ingresos Brutos · inscripción, agentes, retención/percepción y/o certificados según portal jurisdiccional | [obtener](https://www.dgrsantiago.gov.ar/) | [formato/instructivo](https://www.dgrsantiago.gov.ar/) | pendiente_relevamiento | alta_y_revalidacion | no aplica / consulta asistida | pendiente_relevamiento_p3 | Confirmar servicio oficial vigente |
| `tierradelfuego_iibb_online` | Tierra del Fuego | AREF Tierra del Fuego | Ingresos Brutos · inscripción, agentes, retención/percepción y/o certificados según portal jurisdiccional | [obtener](https://www.aref.gob.ar/) | [formato/instructivo](https://www.aref.gob.ar/) | pendiente_relevamiento | alta_y_revalidacion | no aplica / consulta asistida | pendiente_relevamiento_p3 | Confirmar servicio oficial vigente |

## Checklist por fuente antes de automatizar

Para que una fuente pase de `catalogado` a `integrado` debe tener:

- URL oficial de descarga o método oficial de acceso confirmado.
- URL oficial de formato, instructivo, norma, ayuda o layout confirmado.
- Muestra real importada sin modificar manualmente.
- Layout específico o regla de detección genérica documentada.
- Validaciones mínimas: CUIT de 11 dígitos, vigencia, alícuota/régimen, cantidad de filas, duplicados, cambios contra período anterior.
- Manifest con hash y evidencia de origen.
- Casos de prueba reales, idealmente con CUITs presentes en más de un padrón.

## Cómo agregar una nueva fuente

1. Agregar entrada a `config/fuentes_catalogo.json` con `id` estable, jurisdicción, organismo, alcance, URL, modo de descarga, frecuencia, requisitos y mantenimiento seguro.
2. Si el archivo tiene formato propio, agregar layout en `config/padron_layouts.json` con `fuente_id`, campos, separador, tipos y validaciones.
3. Actualizar este registro con link de obtención, link de formato/instructivo y estado.
4. Agregar test/golden sample sintético o sanitizado; los archivos reales grandes quedan fuera de Git.
5. Ejecutar importación en modo previsualización y luego en job async.

## Pendientes de relevamiento profundo

- Separar, cuando el organismo los publique en páginas distintas, los links de descarga del padrón y los links de layout/instructivo/norma.
- Completar layouts específicos para ARBA, ATER Entre Ríos, Córdoba, Santa Fe y cualquier provincia que entregue archivo masivo.
- Completar matriz municipal cuando el cliente confirme municipios donde opera, tributos alcanzados y credenciales disponibles.
- Mantener un lote de CUITs reales de demostración por fuente en documentación sanitizada, sin incluir padrones completos en Git.
