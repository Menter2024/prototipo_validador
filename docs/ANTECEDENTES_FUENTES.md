# Antecedentes — fuentes para alta de proveedores

Fuente: planilla interna de relevamiento de consultas, sitios y padrones para alta de proveedores.

Nota: este documento está sanitizado. No incluye rutas locales, carpetas internas ni archivos de trabajo personales.

## Resumen

| Categoría | Cantidad |
|---|---:|
| ARCA | 9 |
| Ingresos Brutos | 13 |
| Tasas municipales | 1 |
| Separadores / notas | 2 |

## Fuentes relevadas

| Fisco | Consulta | Info Aval | Link / fuente | Modo de acceso / propuesta | Más info |
|---|---|---|---|---|---|
| ARCA | Constancia de CUIT | SI | https://seti.afip.gob.ar/padron-puc-constancia-internet/ConsultaConstanciaAction.do | Link, sin clave, CAPTCHA |  |
| ARCA | Fact. Apócrifas | SI | https://servicioscf.afip.gob.ar/facturacion/facturasapocrifas/default.aspx | Link, sin clave, CAPTCHA |  |
| ARCA | Cert. Ganancias | SI | https://servicioscf.afip.gob.ar/Publico/rg830/rg830.aspx | Link, sin clave, CAPTCHA |  |
| ARCA | Cert. SUSS | SI | https://servicioscf.afip.gob.ar/Publico/NoRetencionSegSoc/Consulta.aspx | Link, sin clave, CAPTCHA |  |
| ARCA | Cert. IVA | SI | https://servicioscf.afip.gob.ar/publico/rg2226/Consulta.aspx | Link, sin clave, CAPTCHA |  |
| ARCA | Agentes de IVA | SI | https://servicioscf.afip.gob.ar/Publico/rg18/rg18.aspx | Link, sin clave, CAPTCHA |  |
| ARCA | Ganancias RG 2681 | SI | https://servicioscf.afip.gob.ar/Publico/Rg2681/consulta.aspx | Link, sin clave, CAPTCHA |  |
| ARCA | CBU informada | SI | https://servicioscf.afip.gob.ar/publico/CbuHabilitadas/consulta.aspx | Link, sin clave, CAPTCHA |  |
| ARCA | Reproweb | NO | Servicio ARCA con CUIT y clave fiscal | Link con clave / posible web service | Manual WS ARCA y referencia AFIPSDK WSAGR |
| Ingresos Brutos | Misiones | NO | https://sinclavefiscal.atm.misiones.gob.ar/sc/ingresos-brutos/constancia-inscripcion | Sólo link |  |
| Ingresos Brutos | Neuquén | NO | https://rentasneuquenweb.gob.ar/nqn/SCF/cons_inscripcion.php | Link público |  |
| Ingresos Brutos | Río Negro | NO | https://agenciaws.rionegro.gov.ar/InscripcionesContribuyente/ | Link, sin clave, CAPTCHA |  |
| Ingresos Brutos | Corrientes | NO | https://www.dgrcorrientes.gob.ar/ | Link, con clave | Servicios / Agentes de Ingresos Brutos / Sujetos a retener y percibir / Consulta por CUIT |
| Tasas municipales | Municipalidad de Córdoba | NO | https://www.tributariomuni.gob.ar/samweb/index.php?r=/objeto/objeto/index&to=2 | Link, sin clave, CAPTCHA | Tributos / Comercios / Identificador |
| Ingresos Brutos | ARBA | SI | https://web.arba.gov.ar/ | Padrón mensual interno | Portal Autogestión - Régimen de Recaudación por sujetos |
| Ingresos Brutos | CABA | SI | https://www.agip.gob.ar/agentes/agentes-de-recaudacion-e-informacion/ | Padrón mensual interno | Padrón Regímenes Generales |
| Ingresos Brutos | Córdoba | NO | https://www.afip.gob.ar/ | Padrón mensual interno | DGR Provincia de Córdoba / Padrones / Agentes / LUA |
| Ingresos Brutos | Entre Ríos | SI | https://www.ater.gob.ar/ater2/PadronAlicuotas.asp | Padrón mensual interno |  |
| Ingresos Brutos | Formosa | NO | https://www.atpformosa.gob.ar/consultas/consulta_categoria_riesgo_fiscal.php?caseid=descarga | Padrón mensual interno |  |
| Ingresos Brutos | Jujuy | NO | https://rentasjujuy.gob.ar/ | Padrón mensual interno | IIBB, padrón con alícuotas de retención/percepción |
| Ingresos Brutos | Mendoza | NO | https://www.atm.mendoza.gov.ar | Padrón mensual interno | IIBB / padrón para agentes de retención y/o percepción |
| Ingresos Brutos | Santa Fe | NO | https://www.afip.gob.ar/ | Padrón mensual interno | API Santa Fe - Sistema Tributario - Contribuyentes, Padrones de IIBB |
| Ingresos Brutos | Tucumán | NO | https://www.afip.gob.ar/ | Padrón mensual interno | Rentas Tucumán, Padrones y Nóminas, padrón de contribuyentes y coeficientes |

## Lectura para roadmap

### Ya cubierto por el prototipo
- Constancia CUIT AFIP/ARCA vía AFIPSDK.
- Lectura base de padrones CSV, hoy con ARBA de ejemplo.
- Exportación Excel consolidada.

### Próximo bloque recomendado
1. **Padrones con archivo mensual**: ARBA, CABA, Entre Ríos primero porque figuran con `Info Aval = SI`.
2. **ARCA con CAPTCHA / links públicos**: Facturas apócrifas, certificados y agentes; evaluar si hay endpoint, scraping asistido, o solo enlace de verificación manual.
3. **Fuentes con clave fiscal o rentas**: dejar para fase posterior por credenciales y riesgo operativo.
4. **Municipal Córdoba**: tratar como fuente separada, no como padrón provincial.
