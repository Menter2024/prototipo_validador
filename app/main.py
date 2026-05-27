"""Backend FastAPI del prototipo Menter — Validación de Alta de Proveedores.

Endpoints:
  GET  /            -> sirve el front HTML
  POST /api/validar -> recibe lista de CUITs y devuelve resultados
  GET  /api/excel/{filename} -> descarga del Excel generado
"""
import os
import asyncio
import base64
import secrets
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import List

import httpx
from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, Response
from pydantic import BaseModel

from app.modules import validador, padrones, afip_arca, georef, excel, fuentes_online, riesgo_fiscal, legajos, carga_masiva, padron_manifest, matriz_tributaria, fuentes_catalogo, descarga_fuentes, fuentes_pendientes, regimenes_catalogo, regimenes_aplicables, accesos_fiscales, supabase_mvp

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
from scripts.importar_padron import importar_padron  # noqa: E402


# Carga .env manualmente (sin dependencia extra)
ENV_FILE = Path(__file__).parent.parent / ".env"
if ENV_FILE.exists():
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

PADRONES_DIR = Path(os.environ.get("PADRONES_DIR", "./padrones")).resolve()
SALIDAS_DIR = Path(os.environ.get("SALIDAS_DIR", "./salidas")).resolve()
SALIDAS_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR = Path(os.environ.get("UPLOADS_DIR", "./uploads")).resolve()
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
EVIDENCIAS_FUENTES_DIR = SALIDAS_DIR / "evidencias" / "fuentes"

app = FastAPI(title="Menter · Validación de Alta de Proveedores")


class ValidarRequest(BaseModel):
    cuits: List[str]


def _padrones_estado() -> list[dict]:
    manifest = padron_manifest.cargar_manifest(PADRONES_DIR)
    estado = []
    for key, cfg in padrones.PADRONES_PROVINCIAS.items():
        item = {
            "key": key,
            "nombre": cfg["nombre"],
            "prioridad": cfg["prioridad"],
            "tipo": cfg["tipo"],
            "archivo": cfg.get("archivo"),
            "url": cfg.get("url"),
            "status": "consulta_manual" if cfg["tipo"] != "archivo" else "no_disponible",
            "registros": None,
            "actualizado": None,
            "periodo": "",
            "vigencia_hasta": "",
            "vigencia_estado": "sin_vigencia",
        }
        meta = manifest.get("padrones", {}).get(key, {})
        if meta:
            item["periodo"] = meta.get("periodo", "")
            item["vigencia_hasta"] = meta.get("vigencia_hasta", "")
            item["vigencia_estado"] = padron_manifest.estado_vigencia(meta.get("vigencia_hasta"))
            item["calidad_estado"] = meta.get("calidad", {}).get("estado", "")
            item["sha256"] = meta.get("sha256", "")
        if cfg["tipo"] == "archivo":
            archivo = PADRONES_DIR / cfg["archivo"]
            if archivo.exists():
                item["status"] = "disponible"
                item["actualizado"] = datetime.fromtimestamp(archivo.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                try:
                    item["registros"] = len(padrones._leer_padron(archivo))
                except Exception:
                    item["status"] = "error"
        estado.append(item)
    return estado


def _basic_auth_habilitada() -> bool:
    return bool(os.environ.get("BASIC_AUTH_USER") and os.environ.get("BASIC_AUTH_PASS"))


def _credenciales_validas(header: str | None) -> bool:
    if not _basic_auth_habilitada():
        return True
    if not header or not header.startswith("Basic "):
        return False
    try:
        usuario_pass = base64.b64decode(header.split(" ", 1)[1]).decode("utf-8")
        usuario, password = usuario_pass.split(":", 1)
    except Exception:
        return False
    return (
        secrets.compare_digest(usuario, os.environ["BASIC_AUTH_USER"])
        and secrets.compare_digest(password, os.environ["BASIC_AUTH_PASS"])
    )


@app.middleware("http")
async def basic_auth_middleware(request: Request, call_next):
    if request.url.path in ("/healthz", "/api/info"):
        return await call_next(request)
    if not _credenciales_validas(request.headers.get("Authorization")):
        return Response(
            status_code=401,
            headers={"WWW-Authenticate": 'Basic realm="Menter Validador"'},
            content="Autenticación requerida",
        )
    return await call_next(request)


async def _procesar_cuit(cuit: str) -> dict:
    """Procesa un CUIT en sus 3 etapas: validación matemática, AFIP, padrones."""
    val = validador.validar(cuit)
    resultado = {
        "cuit": val["cuit"],
        "cuit_limpio": val["cuit_limpio"],
        "valido": val["valido"],
        "tipo_persona": val["tipo"],
        "mensaje_validador": val["mensaje"],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    if not val["valido"]:
        resultado["afip"] = {
            "razon_social": "—",
            "estado_clave": "—",
            "detalle": "No se consultó AFIP porque el CUIT es inválido.",
        }
        resultado["padrones"] = {}
        resultado["georef"] = {"provincia": None}
        resultado["modo_afip"] = "skip"
        return resultado

    # Llamadas en paralelo (asyncio) — wrapper para funciones sync
    loop = asyncio.get_event_loop()
    afip_task = loop.run_in_executor(None, afip_arca.consultar_constancia, val["cuit_limpio"])
    padrones_task = loop.run_in_executor(None, padrones.consultar_todos, val["cuit_limpio"], PADRONES_DIR)
    fuentes_task = loop.run_in_executor(None, fuentes_online.consultar_todas, val["cuit_limpio"])
    afip_data, padrones_data, fuentes_data = await asyncio.gather(afip_task, padrones_task, fuentes_task)

    resultado["afip"] = afip_data
    resultado["padrones"] = padrones_data
    resultado["fuentes_online"] = fuentes_data
    resultado["modo_afip"] = afip_data.get("modo", "demo")

    # Georef sobre el domicilio fiscal
    dom = afip_data.get("domicilio_fiscal", "")
    geo = await loop.run_in_executor(None, georef.normalizar_provincia, dom)
    resultado["georef"] = geo
    resultado["decision_fiscal"] = riesgo_fiscal.evaluar(resultado)
    resultado["matriz_tributaria"] = matriz_tributaria.generar(resultado)

    return resultado


def _agregar_regimenes_aplicables(resultados: list[dict]) -> None:
    fuentes_estado_actual = fuentes_catalogo.evaluar_fuentes(PADRONES_DIR)
    for resultado in resultados:
        resultado["regimenes_aplicables"] = regimenes_aplicables.generar(resultado, fuentes_estado_actual)


@app.post("/api/validar")
async def validar_endpoint(req: ValidarRequest):
    if not req.cuits:
        raise HTTPException(status_code=400, detail="Lista de CUITs vacía.")
    if len(req.cuits) > 50:
        raise HTTPException(status_code=400, detail="Máximo 50 CUITs por solicitud en este prototipo.")

    tareas = [_procesar_cuit(c) for c in req.cuits]
    resultados = await asyncio.gather(*tareas)
    _agregar_regimenes_aplicables(resultados)

    # Generar Excel
    filename = f"validacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    ruta = SALIDAS_DIR / filename
    excel.generar(resultados, ruta)
    legajo = legajos.crear_legajo(resultados, filename, SALIDAS_DIR)
    tareas_asistidas = fuentes_pendientes.crear_desde_resultados(SALIDAS_DIR, resultados, legajo["id"])

    return {
        "resultados": resultados,
        "excel": filename,
        "legajo_id": legajo["id"],
        "tareas_asistidas": len(tareas_asistidas),
        "modo_general": "live" if any(r.get("modo_afip") == "live" for r in resultados) else "demo",
        "total_procesados": len(resultados),
        "total_validos": sum(1 for r in resultados if r.get("valido")),
        "total_live": sum(1 for r in resultados if r.get("modo_afip") == "live"),
        "total_observados": sum(
            1
            for r in resultados
            if r.get("decision_fiscal", {}).get("estado") != "APROBABLE"
            or (not r.get("valido"))
            or r.get("afip", {}).get("en_apoc")
            or (
                r.get("afip", {}).get("estado_clave") not in (None, "—", "ACTIVO")
            )
            or any(p.get("status") == "inscripto" for p in r.get("padrones", {}).values())
        ),
    }


@app.post("/api/validar-excel")
async def validar_excel_endpoint(
    archivo: UploadFile = File(...),
    columna: str | None = Form(None),
    sheet: str | None = Form(None),
):
    if not archivo.filename:
        raise HTTPException(status_code=400, detail="Archivo requerido.")
    ext = Path(archivo.filename).suffix.lower()
    if ext not in {".csv", ".txt", ".tsv", ".psv", ".xlsx", ".xlsm"}:
        raise HTTPException(status_code=400, detail="Formato no soportado. Usá Excel o CSV/TXT.")
    tmp = UPLOADS_DIR / f"lote_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{Path(archivo.filename).name}"
    try:
        with tmp.open("wb") as f:
            shutil.copyfileobj(archivo.file, f)
        cuits = carga_masiva.leer_cuits(tmp, columna or None, sheet or None)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    if not cuits:
        raise HTTPException(status_code=400, detail="No encontré CUITs válidos en el archivo.")
    if len(cuits) > 500:
        raise HTTPException(status_code=400, detail="Máximo 500 CUITs por lote en esta versión.")

    resultados = await asyncio.gather(*[_procesar_cuit(c) for c in cuits])
    _agregar_regimenes_aplicables(resultados)
    filename = f"validacion_lote_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    ruta = SALIDAS_DIR / filename
    excel.generar(resultados, ruta)
    legajo = legajos.crear_legajo(resultados, filename, SALIDAS_DIR)
    tareas_asistidas = fuentes_pendientes.crear_desde_resultados(SALIDAS_DIR, resultados, legajo["id"])
    return {
        "resultados": resultados,
        "excel": filename,
        "legajo_id": legajo["id"],
        "tareas_asistidas": len(tareas_asistidas),
        "modo_general": "live" if any(r.get("modo_afip") == "live" for r in resultados) else "demo",
        "total_procesados": len(resultados),
        "total_validos": sum(1 for r in resultados if r.get("valido")),
        "total_live": sum(1 for r in resultados if r.get("modo_afip") == "live"),
        "total_observados": sum(1 for r in resultados if r.get("decision_fiscal", {}).get("estado") != "APROBABLE"),
    }


@app.get("/api/excel/{filename}")
def descargar_excel(filename: str):
    ruta = SALIDAS_DIR / filename
    if not ruta.exists() or ".." in filename or "/" in filename:
        raise HTTPException(status_code=404, detail="Archivo no encontrado.")
    return FileResponse(
        ruta,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=filename,
    )


@app.get("/api/legajos")
def listar_legajos_endpoint():
    return {"legajos": legajos.listar_legajos(SALIDAS_DIR)}


@app.get("/api/legajos/{legajo_id}")
def obtener_legajo_endpoint(legajo_id: str):
    legajo = legajos.obtener_legajo(SALIDAS_DIR, legajo_id)
    if not legajo:
        raise HTTPException(status_code=404, detail="Legajo no encontrado.")
    return legajo


@app.get("/api/info")
def info():
    """Diagnóstico: muestra configuración y archivos disponibles."""
    return {
        "afip_modo": "live" if os.environ.get("AFIPSDK_TOKEN") else "demo",
        "padrones_dir": str(PADRONES_DIR),
        "padrones_disponibles": sorted(p.name for p in PADRONES_DIR.glob("*.csv")) if PADRONES_DIR.exists() else [],
        "salidas_dir": str(SALIDAS_DIR),
        "supabase": supabase_mvp.status(),
    }


@app.get("/api/mvp/status")
def mvp_status():
    return {
        "storage": "supabase" if supabase_mvp.enabled() else "local",
        "supabase": supabase_mvp.status(),
        "padrones_locales": len(_padrones_estado()),
        "salidas_dir": str(SALIDAS_DIR),
    }


@app.get("/api/padrones")
def padrones_estado():
    manifest = padron_manifest.cargar_manifest(PADRONES_DIR)
    return {"padrones": _padrones_estado(), "historial": manifest.get("historial", [])[:20]}


@app.get("/api/fuentes")
def fuentes_estado():
    estado = fuentes_catalogo.evaluar_fuentes(PADRONES_DIR)
    estado["descargas"] = descarga_fuentes.cargar_manifest(EVIDENCIAS_FUENTES_DIR).get("descargas", [])[:20]
    return estado


@app.get("/api/regimenes")
def regimenes_estado(
    nivel: str | None = None,
    tipo: str | None = None,
    prioridad: str | None = None,
    automatizacion: str | None = None,
    estado_integracion: str | None = None,
    riesgo_operativo: str | None = None,
):
    fuentes_estado_actual = fuentes_catalogo.evaluar_fuentes(PADRONES_DIR)
    return regimenes_catalogo.evaluar_regimenes(
        fuentes_estado_actual,
        nivel=nivel,
        tipo=tipo,
        prioridad=prioridad,
        automatizacion=automatizacion,
        estado_integracion=estado_integracion,
        riesgo_operativo=riesgo_operativo,
    )


@app.get("/api/fuentes-pendientes")
def listar_fuentes_pendientes(estado: str | None = None):
    return fuentes_pendientes.listar(SALIDAS_DIR, estado)


@app.get("/api/accesos")
def listar_accesos(cliente: str | None = None, cuit_agente: str | None = None, organismo: str | None = None):
    fuentes_estado_actual = fuentes_catalogo.evaluar_fuentes(PADRONES_DIR)
    return {
        **accesos_fiscales.listar(SALIDAS_DIR, cliente, cuit_agente, organismo),
        "requisitos": accesos_fiscales.matriz_requisitos(SALIDAS_DIR, fuentes_estado_actual),
    }


@app.post("/api/accesos")
async def crear_acceso(
    cliente: str = Form(...),
    cuit_agente: str = Form(...),
    organismo: str = Form(...),
    servicio: str = Form(...),
    tipo_acceso: str = Form(...),
    estado: str = Form("pendiente"),
    fuente_id: str = Form(""),
    alcance: str = Form(""),
    responsable: str = Form(""),
    notas: str = Form(""),
    evidencia: UploadFile | None = File(None),
):
    tmp = None
    try:
        if evidencia and evidencia.filename:
            tmp = UPLOADS_DIR / f"acceso_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{Path(evidencia.filename).name}"
            with tmp.open("wb") as f:
                shutil.copyfileobj(evidencia.file, f)
        acceso = accesos_fiscales.crear_o_actualizar(
            SALIDAS_DIR,
            cliente,
            cuit_agente,
            organismo,
            servicio,
            tipo_acceso,
            estado,
            fuente_id,
            alcance,
            responsable,
            notas,
            tmp,
            evidencia.filename if evidencia else None,
        )
        supabase_sync = {"enabled": False, "synced": False}
        try:
            supabase_sync = supabase_mvp.sync_acceso(acceso)
        except Exception as sync_error:
            supabase_sync = {"enabled": supabase_mvp.enabled(), "synced": False, "error": str(sync_error)}
        return {"ok": True, "acceso": acceso, "supabase_sync": supabase_sync}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.post("/api/fuentes-pendientes/{item_id}/actualizar")
async def actualizar_fuente_pendiente(
    item_id: str,
    estado: str = Form(...),
    nota: str = Form(""),
    evidencia: UploadFile | None = File(None),
):
    tmp = None
    try:
        if evidencia and evidencia.filename:
            tmp = UPLOADS_DIR / f"evidencia_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{Path(evidencia.filename).name}"
            with tmp.open("wb") as f:
                shutil.copyfileobj(evidencia.file, f)
        item = fuentes_pendientes.actualizar(
            SALIDAS_DIR,
            item_id,
            estado,
            nota,
            tmp,
            evidencia.filename if evidencia else None,
        )
        if not item:
            raise HTTPException(status_code=404, detail="Tarea asistida no encontrada.")
        return {"ok": True, "item": item}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.post("/api/fuentes/descargar")
def descargar_fuente_endpoint(
    fuente_id: str = Form(...),
    dry_run: bool = Form(True),
):
    try:
        return descarga_fuentes.ejecutar_descarga(fuente_id, EVIDENCIAS_FUENTES_DIR, dry_run=dry_run)
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Error consultando fuente: {e}") from e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.post("/api/padrones/importar")
async def importar_padron_endpoint(
    provincia: str = Form(...),
    archivo: UploadFile = File(...),
    sheet: str | None = Form(None),
    periodo: str | None = Form(None),
    vigencia_hasta: str | None = Form(None),
    confirmar_advertencias: bool = Form(False),
    cliente: str = Form(""),
    cuit_agente: str = Form(""),
    fuente_id: str = Form(""),
):
    if not archivo.filename:
        raise HTTPException(status_code=400, detail="Archivo requerido.")
    ext = Path(archivo.filename).suffix.lower()
    if ext not in {".csv", ".txt", ".tsv", ".psv", ".xlsx", ".xlsm", ".zip", ".rar"}:
        raise HTTPException(status_code=400, detail="Formato no soportado. Usá CSV, TXT, XLSX, ZIP o RAR.")
    destino_tmp = UPLOADS_DIR / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{Path(archivo.filename).name}"
    try:
        with destino_tmp.open("wb") as f:
            shutil.copyfileobj(archivo.file, f)
        resultado = importar_padron(
            provincia,
            destino_tmp,
            PADRONES_DIR,
            sheet or None,
            False,
            periodo,
            vigencia_hasta,
            aceptar_observado=confirmar_advertencias,
        )
        supabase_sync = {"enabled": False, "synced": False}
        if cliente and cuit_agente:
            acceso = accesos_fiscales.crear_o_actualizar(
                SALIDAS_DIR,
                cliente,
                cuit_agente,
                provincia,
                f"Carga de padrón {provincia}",
                "archivo_manual",
                "exportacion_manual",
                fuente_id,
                "Carga manual de archivo oficial de padrón.",
                "",
                f"Archivo cargado: {archivo.filename}. Período: {periodo or 's/d'}.",
                destino_tmp,
                archivo.filename,
            )
            try:
                supabase_mvp.sync_acceso(acceso)
            except Exception:
                pass
        try:
            supabase_sync = supabase_mvp.sync_padron_importado(
                archivo_local=destino_tmp,
                provincia=provincia,
                resultado_importacion=resultado,
                cliente=cliente or "CCU",
                fuente_id=fuente_id,
            )
        except Exception as sync_error:
            supabase_sync = {"enabled": supabase_mvp.enabled(), "synced": False, "error": str(sync_error)}
        return {"ok": True, **resultado, "estado": _padrones_estado(), "supabase_sync": supabase_sync}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.post("/api/padrones/previsualizar")
async def previsualizar_padron_endpoint(
    provincia: str = Form(...),
    archivo: UploadFile = File(...),
    sheet: str | None = Form(None),
    periodo: str | None = Form(None),
    vigencia_hasta: str | None = Form(None),
):
    if not archivo.filename:
        raise HTTPException(status_code=400, detail="Archivo requerido.")
    ext = Path(archivo.filename).suffix.lower()
    if ext not in {".csv", ".txt", ".tsv", ".psv", ".xlsx", ".xlsm", ".zip", ".rar"}:
        raise HTTPException(status_code=400, detail="Formato no soportado. Usá CSV, TXT, XLSX, ZIP o RAR.")
    destino_tmp = UPLOADS_DIR / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_preview_{Path(archivo.filename).name}"
    try:
        with destino_tmp.open("wb") as f:
            shutil.copyfileobj(archivo.file, f)
        resultado = importar_padron(provincia, destino_tmp, PADRONES_DIR, sheet or None, True, periodo, vigencia_hasta)
        return {"ok": True, **resultado}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.get("/healthz")
def healthz():
    return {"ok": True}


# Front estático
STATIC_DIR = Path(__file__).parent / "static"


@app.get("/", response_class=HTMLResponse)
def index():
    return (STATIC_DIR / "index.html").read_text(encoding="utf-8")


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page():
    return (STATIC_DIR / "dashboard.html").read_text(encoding="utf-8")


@app.get("/info", response_class=HTMLResponse)
def info_page():
    return (STATIC_DIR / "info.html").read_text(encoding="utf-8")


@app.get("/configuracion", response_class=HTMLResponse)
def configuracion_page():
    return (STATIC_DIR / "configuracion.html").read_text(encoding="utf-8")


@app.get("/padrones", response_class=HTMLResponse)
def padrones_admin():
    return (STATIC_DIR / "padrones.html").read_text(encoding="utf-8")


@app.get("/fuentes", response_class=HTMLResponse)
def fuentes_page():
    return (STATIC_DIR / "fuentes.html").read_text(encoding="utf-8")


@app.get("/regimenes", response_class=HTMLResponse)
def regimenes_page():
    return (STATIC_DIR / "regimenes.html").read_text(encoding="utf-8")


@app.get("/fuentes-pendientes", response_class=HTMLResponse)
def fuentes_pendientes_page():
    return (STATIC_DIR / "fuentes_pendientes.html").read_text(encoding="utf-8")


@app.get("/accesos", response_class=HTMLResponse)
def accesos_page():
    return (STATIC_DIR / "accesos.html").read_text(encoding="utf-8")


@app.get("/legajos", response_class=HTMLResponse)
def legajos_page():
    return (STATIC_DIR / "legajos.html").read_text(encoding="utf-8")


@app.get("/legajos/{legajo_id}", response_class=HTMLResponse)
def legajo_detalle_page(legajo_id: str):
    return (STATIC_DIR / "legajo_detalle.html").read_text(encoding="utf-8")


@app.get("/lotes", response_class=HTMLResponse)
def lotes_page():
    return (STATIC_DIR / "lotes.html").read_text(encoding="utf-8")


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
