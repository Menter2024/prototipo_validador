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

## Formato del CSV

Cabecera obligatoria:

```
cuit,alicuota_retencion,alicuota_percepcion,vigencia_desde,vigencia_hasta
```

Ejemplo:

```
30500010912,2.00,3.00,01/05/2026,31/05/2026
```

## Cómo armar el CSV a partir del padrón oficial

Cada provincia entrega el padrón en formato distinto (ARBA en TXT ancho fijo, otras en Excel). En la próxima fase del proyecto se incorpora un conversor automático. Para el prototipo, basta con:

1. Descargar el padrón mensual del sitio oficial.
2. Abrirlo en Excel y dejar las columnas en el orden indicado arriba.
3. Guardar como CSV con codificación UTF-8.
4. Renombrarlo exactamente como figura en la convención.

## Archivo de ejemplo

`PadronARBA.csv` ya viene con datos ficticios para que la demo funcione de entrada. Reemplazalo por el padrón real cuando quieras consultas verdaderas.
