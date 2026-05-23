# Carpeta de padrones provinciales

El sistema lee los padrones de Ingresos Brutos desde esta carpeta.

## Convención de nombres

Cada provincia tiene un archivo CSV con nombre fijo. El sistema busca exactamente estos archivos:

```
PadronARBA.csv         (Buenos Aires)
PadronCABA.csv
PadronCordoba.csv
PadronEntreRios.csv
PadronFormosa.csv
PadronJujuy.csv
PadronMendoza.csv
PadronSantaFe.csv
PadronTucuman.csv
```

Si un archivo falta, el sistema lo reporta como "no_disponible" pero no se detiene.

## Fuentes provinciales sin archivo mensual normalizado

También se informan en la salida, pero no se marcan como "no inscripto" porque requieren consulta online o credenciales:

| Provincia | Estado técnico | Fuente |
|---|---|---|
| Misiones | consulta manual online | https://sinclavefiscal.atm.misiones.gob.ar/sc/ingresos-brutos/constancia-inscripcion |
| Neuquén | consulta manual online | https://rentasneuquenweb.gob.ar/nqn/SCF/cons_inscripcion.php |
| Río Negro | consulta manual / CAPTCHA | https://agenciaws.rionegro.gov.ar/InscripcionesContribuyente/ |
| Corrientes | requiere credenciales | https://www.dgrcorrientes.gob.ar/ |

## Formato CSV canónico

Cabecera recomendada:

```
cuit,alicuota_retencion,alicuota_percepcion,vigencia_desde,vigencia_hasta,regimen
```

Ejemplo:

```
30500010912,2.00,3.00,01/05/2026,31/05/2026,Regimen General
```

`regimen` es opcional.

## Cabeceras alternativas soportadas

El lector también acepta CSV separados por coma, punto y coma, tab o `|`, con codificación UTF-8 o Latin-1.

Alias reconocidos:

| Campo interno | Cabeceras aceptadas |
|---|---|
| `cuit` | `cuit`, `cuit_contribuyente`, `nro_cuit`, `numero_cuit` |
| `alicuota_retencion` | `retencion`, `ali_ret`, `alic_ret`, `alicuota retencion` |
| `alicuota_percepcion` | `percepcion`, `ali_per`, `alic_per`, `alicuota percepcion` |
| `vigencia_desde` | `desde`, `fecha_desde`, `vig desde`, `inicio` |
| `vigencia_hasta` | `hasta`, `fecha_hasta`, `vig hasta`, `fin` |
| `regimen` | `regimen`, `tipo`, `categoria` |

## Prioridad de implementación

Según antecedentes relevados, el primer bloque de padrones a normalizar es:

1. ARBA / Buenos Aires
2. CABA / AGIP
3. Entre Ríos / ATER

El resto queda soportado por convención de nombres, pero se normaliza cuando estén los archivos reales.

## Cómo armar el CSV a partir del padrón oficial

Cada provincia entrega el padrón en formato distinto (ARBA en TXT ancho fijo, otras en Excel/CSV). El repo incluye un importador para normalizar ARBA, CABA y Entre Ríos.

### Importador automático

Uso:

```bash
python scripts/importar_padron.py ARBA /ruta/al/padron_original.txt
python scripts/importar_padron.py CABA /ruta/al/padron_original.xlsx
python scripts/importar_padron.py EntreRios /ruta/al/padron_original.csv
```

Opciones:

```bash
python scripts/importar_padron.py CABA archivo.xlsx --sheet "Hoja1"
python scripts/importar_padron.py ARBA archivo.txt --dry-run
python scripts/importar_padron.py EntreRios archivo.csv --out-dir ./padrones
```

El importador:

- Detecta CSV separado por coma, punto y coma, tab o `|`.
- Lee XLSX.
- Para TXT sin cabecera, intenta detectar CUIT de 11 dígitos y hasta dos alícuotas por línea.
- Deduplica CUITs.
- Escribe el archivo destino con el nombre esperado por el validador.

### Conversión manual

Si el archivo oficial viene en un formato todavía no soportado:

1. Descargar el padrón mensual del sitio oficial.
2. Abrirlo en Excel y dejar las columnas en el orden indicado arriba.
3. Guardar como CSV con codificación UTF-8.
4. Renombrarlo exactamente como figura en la convención.

## Archivo de ejemplo

`PadronARBA.csv` ya viene con datos ficticios para que la demo funcione de entrada. Reemplazalo por el padrón real cuando quieras consultas verdaderas.
