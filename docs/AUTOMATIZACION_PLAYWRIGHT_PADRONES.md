# Automatización Playwright para padrones fiscales

Estado: 2026-05-26

## Objetivo

Usar un navegador real para descargar padrones públicos o capturar evidencia de portales oficiales cuando `curl/httpx` no alcanza por TLS, SPA, formularios GeneXus o flujo de descarga dinámico.

No se usa para eludir CAPTCHA, MFA, restricciones de acceso ni credenciales no autorizadas.

## Instalación local

```bash
.venv/bin/python3.13 -m pip install '.[automation]'
.venv/bin/python3.13 -m playwright install chromium
```

Los browsers de Playwright y archivos `storage_state` no deben commitearse.

## Configuración

Los adaptadores viven en:

- `config/portal_adapters.json`

Tipos soportados:

| Tipo | Uso | Política |
|---|---|---|
| `public_download` | Click en link/botón de descarga pública | Ejecutable sin credenciales. |
| `public_query` | Consulta pública por CUIT | Ejecutable si no hay CAPTCHA/MFA. |
| `authenticated_download` | Portal con clave fiscal/CIT | Requiere `--allow-authenticated` y autorización. |
| `captcha_blocked` | Portal con CAPTCHA | No se automatiza; cola asistida. |

## CLI

Dry-run sin abrir navegador:

```bash
.venv/bin/python3.13 scripts/descargar_portal.py jujuy_iibb_padron_publico \
  --periodo 2026-06 \
  --dry-run
```

Descarga pública Jujuy:

```bash
.venv/bin/python3.13 scripts/descargar_portal.py jujuy_iibb_padron_publico \
  --periodo 2026-06 \
  --headed
```

Descarga pública AGIP/CABA por texto visible:

```bash
.venv/bin/python3.13 scripts/descargar_portal.py agip_caba_regimenes_generales_publico \
  --periodo 2026-06 \
  --vigencia-text 01/06/2026 \
  --headed
```

Portal autenticado con sesión previamente guardada:

```bash
.venv/bin/python3.13 scripts/descargar_portal.py arba_iibb_padron_autenticado \
  --periodo 2026-06 \
  --allow-authenticated \
  --storage-state /ruta/segura/arba.storage_state.json \
  --headed
```

## Evidencia generada

Cada ejecución crea una carpeta bajo:

- `padrones/originales/portal/{adapter_id}/{timestamp}/`

Contenido esperado:

- `downloads/` archivos descargados.
- `screenshots/` capturas.
- `html/final.html`.
- `trace.zip`.
- `evidencia.json` con hash SHA256, URL, timestamps y estado.

## Credenciales y sesiones

Playwright permite reutilizar sesiones con `storage_state`. Ese archivo contiene cookies/tokens y puede permitir impersonación del usuario.

Reglas:

1. Guardarlo fuera del repo.
2. Cifrarlo si se persiste.
3. Separarlo por cliente/fuente.
4. Vencerlo o rotarlo periódicamente.
5. Registrar autorización y servicio delegado.
6. No commitear `playwright/.auth/` ni `*.storage_state.json`.

## Priorización recomendada

1. `jujuy_iibb_padron_publico`: formulario público GeneXus.
2. `agip_caba_regimenes_generales_publico`: fallback a navegador real si `curl` falla.
3. `agip_caba_alicuotas_diferenciales_publico`: idem.
4. `misiones_iibb_constancia_publica`: completar selector CUIT tras exploración.
5. `arba_iibb_padron_autenticado`: sólo con CIT/servicio delegado del cliente piloto.
6. `comarb_sircreb_autenticado`: sólo con Portal Federal autorizado.

## Integración posterior

Luego de una descarga exitosa:

1. Ubicar archivo descargado en `padrones/originales/portal/.../downloads`.
2. Importar con `scripts/importar_padron.py` si el parser existe.
3. Si parser no existe, crear fixture controlado y parser jurisdiccional.
4. Registrar en manifest con hash y calidad.
5. Revalidar proveedores en `/api/validar`.
