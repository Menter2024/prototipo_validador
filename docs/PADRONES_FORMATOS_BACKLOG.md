# Backlog de formatos y layouts de padrones

Actualizado: 2026-06-04.

Este backlog convierte el registro maestro en trabajo verificable: identifica qué fuentes ya tienen layout específico, cuáles requieren relevar archivo real y cuáles son consultas/API/cola asistida.

## Resumen

- Fuentes auditadas: 34
- consulta_api_o_asistida: 25
- layout_especifico: 9

## Matriz completa

| Prioridad | Fuente | Jurisdicción | Tipo | Obtención | Estado formato | Layout | Bloquea masivo | Próxima acción |
|---|---|---|---|---|---|---|---|---|
| P0 | `arba_iibb` | Buenos Aires | archivo_normalizado | [link](https://web.arba.gov.ar/regimen-de-recaudacion-por-sujeto) | landing_con_instructivo_a_verificar | `arba_iibb_sujeto_csv_v1` | no | Mantener muestra real, hash, golden CUITs y alerta de cambio de columnas. |
| P0 | `agip_caba_iibb` | CABA | archivo_normalizado | [link](https://imagenes.agip.gob.ar/agentes/agentes-de-recaudacion-e-informacion) | landing_con_instructivo_a_verificar | `agip_caba_regimenes_generales_v1` | no | Mantener muestra real, hash, golden CUITs y alerta de cambio de columnas. |
| P0 | `comarb_sircip` | Convenio Multilateral | requiere_credenciales | [link](https://www.ca.gob.ar/sistemas/sircip) | landing_con_instructivo_a_verificar | consulta_api_o_asistida | no | Documentar contrato/API/playbook de acceso y evidencia; no requiere layout masivo inicial. |
| P0 | `comarb_sircreb` | Convenio Multilateral | requiere_credenciales | [link](https://www.ca.gob.ar/index.php/sistemas/sircreb) | landing_con_instructivo_a_verificar | consulta_api_o_asistida | no | Documentar contrato/API/playbook de acceso y evidencia; no requiere layout masivo inicial. |
| P0 | `comarb_sircupa` | Convenio Multilateral | requiere_credenciales | [link](https://www.ca.gob.ar/sistemas/sircupa) | landing_con_instructivo_a_verificar | consulta_api_o_asistida | no | Documentar contrato/API/playbook de acceso y evidencia; no requiere layout masivo inicial. |
| P0 | `ater_entrerios_iibb` | Entre Ríos | archivo_normalizado | [link](https://www.ater.gov.ar/ater2/NominasAgentes.asp) | landing_con_instructivo_a_verificar | `ater_entrerios_iibb_csv_v1` | no | Mantener muestra real, hash, golden CUITs y alerta de cambio de columnas. |
| P0 | `arca_apoc` | Nacional | requiere_navegador | [link](https://www.arca.gob.ar/facturacion/default.asp) | landing_con_instructivo_a_verificar | consulta_api_o_asistida | no | Documentar contrato/API/playbook de acceso y evidencia; no requiere layout masivo inicial. |
| P0 | `arca_constancia` | Nacional | automatizada | [link](https://www.afip.gob.ar/ws/) | landing_con_instructivo_a_verificar | consulta_api_o_asistida | no | Documentar contrato/API/playbook de acceso y evidencia; no requiere layout masivo inicial. |
| P0 | `arca_sire` | Nacional | requiere_credenciales | [link](https://arca.gob.ar/sire/) | landing_con_instructivo_a_verificar | consulta_api_o_asistida | no | Documentar contrato/API/playbook de acceso y evidencia; no requiere layout masivo inicial. |
| P0 | `santafe_iibb` | Santa Fe | archivo_normalizado | [link](https://www.santafe.gob.ar/index.php/web/content/view/full/221362/(subtema)/102284) | landing_con_instructivo_a_verificar | `santafe_iibb_parp_delimitado_v1` | no | Mantener muestra real, hash, golden CUITs y alerta de cambio de columnas. |
| P1 | `chubut_iibb_agentes` | Chubut | pendiente_automatizacion | [link](https://www.dgrchubut.gov.ar/agentes-de-retencion-y-percepcion/) | landing_con_instructivo_a_verificar | consulta_api_o_asistida | no | Documentar contrato/API/playbook de acceso y evidencia; no requiere layout masivo inicial. |
| P1 | `comarb_sifere_padron` | Convenio Multilateral | requiere_credenciales | [link](https://www.ca.gob.ar/sistemas/padron-web-padron-federal) | landing_con_instructivo_a_verificar | consulta_api_o_asistida | no | Documentar contrato/API/playbook de acceso y evidencia; no requiere layout masivo inicial. |
| P1 | `comarb_sircar` | Convenio Multilateral | requiere_credenciales | [link](https://www.ca.gob.ar/sistemas/sircar) | landing_con_instructivo_a_verificar | consulta_api_o_asistida | no | Documentar contrato/API/playbook de acceso y evidencia; no requiere layout masivo inicial. |
| P1 | `comarb_sirtac` | Convenio Multilateral | requiere_credenciales | [link](https://www.ca.gob.ar/sistemas/sirtac) | landing_con_instructivo_a_verificar | consulta_api_o_asistida | no | Documentar contrato/API/playbook de acceso y evidencia; no requiere layout masivo inicial. |
| P1 | `corrientes_iibb_online` | Corrientes | requiere_credenciales | [link](https://www.dgrcorrientes.gov.ar/rentascorrientes/consultarContenido.do?categoria=199) | landing_con_instructivo_a_verificar | consulta_api_o_asistida | no | Documentar contrato/API/playbook de acceso y evidencia; no requiere layout masivo inicial. |
| P1 | `cordoba_iibb` | Córdoba | archivo_normalizado | [link](https://www.rentascordoba.gob.ar/cms/ms-agentes/) | landing_con_instructivo_a_verificar | `cordoba_iibb_delimitado_v1` | no | Mantener muestra real, hash, golden CUITs y alerta de cambio de columnas. |
| P1 | `jujuy_iibb` | Jujuy | archivo_normalizado | [link](https://rentasjujuy.gob.ar/agentes-ingresos-brutos/) | landing_con_instructivo_a_verificar | `jujuy_iibb_xlsx_alias_v1` | no | Mantener muestra real, hash, golden CUITs y alerta de cambio de columnas. |
| P1 | `mendoza_iibb` | Mendoza | archivo_normalizado | [link](https://www.atm.mendoza.gov.ar/) | link_descarga_diferente_de_url_base | `mendoza_iibb_retib_delimitado_v1` | no | Mantener muestra real, hash, golden CUITs y alerta de cambio de columnas. |
| P1 | `misiones_iibb_online` | Misiones | requiere_navegador | [link](https://sinclavefiscal.atm.misiones.gob.ar/sc/ingresos-brutos/constancia-inscripcion) | landing_con_instructivo_a_verificar | consulta_api_o_asistida | no | Documentar contrato/API/playbook de acceso y evidencia; no requiere layout masivo inicial. |
| P1 | `rionegro_iibb_online` | Río Negro | requiere_captcha | [link](https://agenciaws.rionegro.gov.ar/InscripcionesContribuyente/) | landing_con_instructivo_a_verificar | consulta_api_o_asistida | no | Documentar contrato/API/playbook de acceso y evidencia; no requiere layout masivo inicial. |
| P1 | `tucuman_iibb` | Tucumán | archivo_normalizado | [link](https://www.rentastucuman.gob.ar/) | landing_con_instructivo_a_verificar | `tucuman_iibb_rg23_csv_v1`, `tucuman_padron_contribuyente_txt_v1`, `tucuman_coef_rg116_txt_v1` | no | Mantener muestra real, hash, golden CUITs y alerta de cambio de columnas. |
| P2 | `catamarca_iibb_online` | Catamarca | pendiente_automatizacion | [link](https://arcat.gob.ar/) | landing_con_instructivo_a_verificar | consulta_api_o_asistida | no | Documentar contrato/API/playbook de acceso y evidencia; no requiere layout masivo inicial. |
| P2 | `chaco_iibb_online` | Chaco | pendiente_automatizacion | [link](https://atp.chaco.gob.ar/) | landing_con_instructivo_a_verificar | consulta_api_o_asistida | no | Documentar contrato/API/playbook de acceso y evidencia; no requiere layout masivo inicial. |
| P2 | `formosa_iibb` | Formosa | archivo_normalizado | [link](https://www.formosa.gob.ar/tramite/120/inscripcion_como_agente_de_percepcion_del_impuesto_sobre_los_ingresos_brutos) | landing_con_instructivo_a_verificar | `formosa_iibb_delimitado_v1` | no | Mantener muestra real, hash, golden CUITs y alerta de cambio de columnas. |
| P2 | `lapampa_iibb_online` | La Pampa | pendiente_automatizacion | [link](https://www.dgr.lapampa.gob.ar/) | landing_con_instructivo_a_verificar | consulta_api_o_asistida | no | Documentar contrato/API/playbook de acceso y evidencia; no requiere layout masivo inicial. |
| P2 | `larioja_iibb_online` | La Rioja | pendiente_automatizacion | [link](https://dgip.larioja.gob.ar/) | landing_con_instructivo_a_verificar | consulta_api_o_asistida | no | Documentar contrato/API/playbook de acceso y evidencia; no requiere layout masivo inicial. |
| P2 | `salta_iibb_online` | Salta | pendiente_automatizacion | [link](https://www.dgrsalta.gov.ar/) | landing_con_instructivo_a_verificar | consulta_api_o_asistida | no | Documentar contrato/API/playbook de acceso y evidencia; no requiere layout masivo inicial. |
| P2 | `sanjuan_iibb_online` | San Juan | pendiente_automatizacion | [link](https://rentas.dgrsj.gob.ar/) | landing_con_instructivo_a_verificar | consulta_api_o_asistida | no | Documentar contrato/API/playbook de acceso y evidencia; no requiere layout masivo inicial. |
| P2 | `sanluis_iibb_online` | San Luis | pendiente_automatizacion | [link](https://dpip.sanluis.gov.ar/) | landing_con_instructivo_a_verificar | consulta_api_o_asistida | no | Documentar contrato/API/playbook de acceso y evidencia; no requiere layout masivo inicial. |
| P3 | `municipal_padrones_huella_cliente` | Municipal | priorizar_por_huella_cliente | [link](https://www.argentina.gob.ar/municipios) | landing_con_instructivo_a_verificar | consulta_api_o_asistida | no | Documentar contrato/API/playbook de acceso y evidencia; no requiere layout masivo inicial. |
| P3 | `neuquen_iibb_online` | Neuquén | automatizada | [link](https://rentasneuquenweb.gob.ar/nqn/SCF/cons_inscripcion.php) | landing_con_instructivo_a_verificar | consulta_api_o_asistida | no | Documentar contrato/API/playbook de acceso y evidencia; no requiere layout masivo inicial. |
| P3 | `santacruz_iibb_online` | Santa Cruz | pendiente_automatizacion | [link](https://asip.gob.ar/) | landing_con_instructivo_a_verificar | consulta_api_o_asistida | no | Documentar contrato/API/playbook de acceso y evidencia; no requiere layout masivo inicial. |
| P3 | `santiago_iibb_online` | Santiago del Estero | pendiente_automatizacion | [link](https://www.dgrsantiago.gov.ar/) | landing_con_instructivo_a_verificar | consulta_api_o_asistida | no | Documentar contrato/API/playbook de acceso y evidencia; no requiere layout masivo inicial. |
| P3 | `tierradelfuego_iibb_online` | Tierra del Fuego | pendiente_automatizacion | [link](https://www.aref.gob.ar/) | landing_con_instructivo_a_verificar | consulta_api_o_asistida | no | Documentar contrato/API/playbook de acceso y evidencia; no requiere layout masivo inicial. |

## Orden de trabajo recomendado

1. Mantener layouts validados con muestras reales, hash, golden CUITs y alerta de cambio de columnas.
2. Validar nuevas versiones mensuales contra estos layouts antes de promoverlas.
3. Completar nuevas fuentes masivas que incorpore el cliente.
4. Consultas/API/portales: documentar playbook, credenciales, evidencia y límites legales/técnicos.
5. Municipales: abrir subregistro por municipios reales del cliente.

## Criterio de terminado por fuente

- Link oficial de obtención confirmado.
- Instructivo/layout/norma o muestra real con columnas documentadas.
- `layout_id` específico si hay archivo masivo.
- Test unitario del traductor y golden sample sanitizado.
- Manifest con hash de original y validaciones de calidad.
