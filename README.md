# Prototipo Menter — Validador de Alta de Proveedores

Backend Python (FastAPI) + front HTML que muestra cómo funcionaría la solución completa para CCU Argentina. Hace consultas reales contra APIs públicas y muestra resultados en Excel.

## Qué hace de verdad este prototipo

Tres módulos funcionan al 100% sin que tengas que configurar nada:

**Validación matemática del CUIT.** Verifica el dígito verificador con el algoritmo oficial de AFIP. Funciona offline contra cualquier CUIT. Permite descartar CUITs mal escritos antes de gastar tiempo consultando.

**Lectura de padrones provinciales.** Lee archivos CSV de la carpeta `padrones/`. Ya viene un padrón ARBA de ejemplo. Cuando reemplaces los archivos por padrones reales, la búsqueda es real.

**Validación de provincia con georef.** Consulta la API pública de `apis.datos.gob.ar` para normalizar la provincia del domicilio. Es una API gubernamental argentina real, sin auth.

Y un módulo que arranca en modo demo y se vuelve "live" cuando configurás credenciales:

**Consulta a AFIP/ARCA vía afipsdk.com.** Si dejás vacío el token, devuelve datos demo de tres CUITs conocidos (AFIP, Banco Nación, YPF). Si registrás una cuenta en afipsdk.com (gratis hasta cierto volumen) y pegás el token en `.env`, el sistema consulta en tiempo real contra Padrón Constancia de Inscripción.

## Instalación paso a paso

### 1. Requisitos previos

Ya tenés instalado todo lo que se necesita: `uv` está en `/Users/berna/.local/bin/uv` y se encarga del resto.

### 2. Descomprimir el proyecto

Descomprimí la carpeta `prototipo_validador` donde quieras. Por ejemplo en `~/projects/`.

### 3. Arrancar el servidor

Abrí Terminal y ejecutá estos dos comandos:

```bash
cd ~/projects/prototipo_validador
bash run.sh
```

La primera vez tarda un poco mientras `uv` instala las dependencias. Cuando termina, vas a ver:

```
==> Arrancando servidor en http://localhost:8000
```

### 4. Abrir el navegador

Andá a [http://localhost:8000](http://localhost:8000). Vas a ver el front del validador.

### 5. Probar

Click en "Cargar CUITs de ejemplo" y después "Validar". Vas a ver tres CUITs reales procesados (AFIP, Banco Nación, YPF) con sus datos. El botón "Descargar Excel" te baja el reporte consolidado.

## Cómo activar el modo "live" (consulta real a AFIP)

Por defecto, el sistema usa datos demo para AFIP. Para que consulte en vivo:

1. Andá a [afipsdk.com](https://afipsdk.com/) y registrate (botón "Comenzar" o "Sign Up"). Es gratis para volumen inicial.
2. Una vez dentro, buscá la sección "API Keys" o "Tokens".
3. Generá un token nuevo y copialo.
4. En la carpeta del proyecto, abrí el archivo `.env` y pegá el token:

```
AFIPSDK_TOKEN=tu_token_aqui
```

5. Detené el server (Ctrl+C) y volvelo a arrancar con `bash run.sh`. Ahora consulta en vivo.

## Deploy en Railway

El repo ya incluye `railway.json` y `requirements.txt` para que Railway detecte Python/FastAPI y arranque con el puerto dinámico que expone la plataforma.

### Opción A: desde GitHub

1. Subí este proyecto a un repo de GitHub.
2. En Railway: **New Project → Deploy from GitHub repo**.
3. Seleccioná el repo y hacé deploy.
4. En el servicio creado: **Settings → Networking → Public Networking → Generate Domain**.
5. Si querés AFIP en vivo, agregá en Railway → **Variables**:

```
AFIPSDK_TOKEN=tu_token_aqui
PADRONES_DIR=./padrones
SALIDAS_DIR=./salidas
```

Para consultar CUITs reales en producción (no homologación/dev), agregá también:

```
AFIPSDK_ENV=prod
AFIPSDK_TAX_ID=CUIT_REPRESENTANTE_SIN_GUIONES
AFIPSDK_CERT=contenido_del_certificado_crt
AFIPSDK_KEY=contenido_de_la_clave_key
```

Si solo cargás `AFIPSDK_TOKEN`, el sistema puede quedar en modo live contra el entorno `dev` de AFIPSDK, pero ese entorno no devuelve datos productivos de cualquier CUIT real.

## Deploy gratis en Render

El repo incluye `render.yaml`. En Render usá **New → Blueprint**, conectá el repo y dejá vacío **Blueprint Path** para que detecte el archivo de la raíz.

Variables secretas requeridas en Render:

```
AFIPSDK_TOKEN
AFIPSDK_CERT_PEM
AFIPSDK_KEY_PEM
BASIC_AUTH_USER
BASIC_AUTH_PASS
```

`AFIPSDK_CERT_PEM` y `AFIPSDK_KEY_PEM` pueden pegarse con saltos de línea reales o con `\n`. Si el dashboard rompe el formato, usá `AFIPSDK_CERT_B64` y `AFIPSDK_KEY_B64` como alternativa manual.

El sitio queda protegido con Basic Auth; `/healthz` queda público solo para que Render pueda verificar el servicio.

### Opción B: desde Railway CLI

```bash
railway login
railway init
railway up
```

Después generá el dominio público desde **Settings → Networking**.

## Cómo cargar padrones provinciales reales

Mirá `padrones/README.md`. Resumen: bajás el padrón mensual del sitio oficial (ARBA, AGIP, etc.), lo convertís a CSV con la cabecera correcta, y lo guardás con el nombre fijo en la carpeta `padrones/`.

También podés usar el importador:

```bash
python scripts/importar_padron.py ARBA /ruta/al/padron_original.txt
python scripts/importar_padron.py CABA /ruta/al/padron_original.xlsx
python scripts/importar_padron.py EntreRios /ruta/al/padron_original.csv
python scripts/importar_padron.py SantaFe /ruta/al/padron_original.csv
```

## Estructura del proyecto

```
prototipo_validador/
├── README.md                  # este archivo
├── pyproject.toml             # dependencias (gestionado por uv)
├── .env.example               # plantilla de configuración
├── run.sh                     # arranque en un comando
│
├── app/
│   ├── main.py                # API FastAPI (endpoints)
│   ├── modules/
│   │   ├── validador.py       # validación matemática CUIT
│   │   ├── afip_arca.py       # consulta AFIP (demo o live)
│   │   ├── padrones.py        # lectura padrones CSV
│   │   ├── georef.py          # API real datos.gob.ar
│   │   └── excel.py           # generación Excel
│   └── static/
│       └── index.html         # front
│
├── padrones/                  # archivos de padrones provinciales
│   ├── README.md
│   └── PadronARBA.csv         # ejemplo con datos ficticios
│
└── salidas/                   # acá se guardan los Excel generados
```

## Endpoints del backend

Si querés usar el backend desde tu propio script o desde n8n:

**POST** `/api/validar`

```json
{ "cuits": ["33-69345023-9", "30-50001091-2"] }
```

Devuelve los resultados estructurados + el nombre del archivo Excel generado.

**GET** `/api/excel/{filename}` — descarga el Excel.

**GET** `/api/info` — diagnóstico (modo actual, padrones disponibles, etc.).

## Qué le mostrás a Luis Ronchi

1. Abrís el front en `localhost:8000`.
2. Cargás los CUITs de ejemplo y mostrás cómo el sistema valida matemáticamente y consulta AFIP + padrones + georef en paralelo, en segundos.
3. Le mostrás el Excel descargado y le explicás que esto es lo que su equipo de Impuestos recibiría en cada alta.
4. Le explicás que el alcance completo (los 23 sitios y padrones) es lo que se construye en las fases 1 y 2 de la propuesta.
5. Le decís: "Este prototipo lo armamos en dos días para que veas la mecánica. La versión productiva, con afipsdk en vivo, los 13 padrones provinciales, los sitios con CAPTCHA y la interfaz pulida para Impuestos, es lo que cotizamos en la propuesta."

## Solución de problemas

**Si el server no arranca:** verificá que `uv` esté en `/Users/berna/.local/bin/uv`. Si no, ajustá la ruta en `run.sh`.

**Si dice "Address already in use":** algún otro proceso está usando el puerto 8000. Cambiá `--port 8000` por `--port 8080` en `run.sh`.

**Si AFIP devuelve siempre demo:** revisá que `AFIPSDK_TOKEN` esté en `.env` (sin espacios) y que reiniciaste el server.

**Si los padrones no aparecen:** verificá que el archivo `PadronARBA.csv` (u otro) esté en la carpeta `padrones/`, con esa cabecera exacta, y guardado como UTF-8.
