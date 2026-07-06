"""Cliente Supabase opcional para MVP barato.

Diseño: FastAPI habla server-side con service_role. Si faltan env vars,
el sistema sigue funcionando localmente sin romper demo/tests.
"""
from __future__ import annotations

import hashlib
import mimetypes
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

DEFAULT_BUCKET = "menter-fiscal"
PADRON_IMPORT_TABLE = "padron_import_jobs"


@dataclass(frozen=True)
class SupabaseConfig:
    url: str
    service_role_key: str
    bucket: str = DEFAULT_BUCKET
    tenant_slug: str = "ccu"


def _clean_url(value: str) -> str:
    return value.strip().rstrip("/")


def get_config() -> SupabaseConfig | None:
    url = _clean_url(os.environ.get("SUPABASE_URL", ""))
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    if not url or not key:
        return None
    return SupabaseConfig(
        url=url,
        service_role_key=key,
        bucket=os.environ.get("SUPABASE_STORAGE_BUCKET", DEFAULT_BUCKET).strip() or DEFAULT_BUCKET,
        tenant_slug=os.environ.get("SUPABASE_TENANT_SLUG", "ccu").strip() or "ccu",
    )


def enabled() -> bool:
    return get_config() is not None


def status() -> dict[str, Any]:
    cfg = get_config()
    return {
        "enabled": cfg is not None,
        "url": cfg.url if cfg else "",
        "bucket": cfg.bucket if cfg else DEFAULT_BUCKET,
        "tenant_slug": cfg.tenant_slug if cfg else os.environ.get("SUPABASE_TENANT_SLUG", "ccu"),
        "service_role_configurado": bool(cfg and cfg.service_role_key),
    }


def _headers(cfg: SupabaseConfig, extra: dict[str, str] | None = None) -> dict[str, str]:
    headers = {
        "apikey": cfg.service_role_key,
        "Authorization": f"Bearer {cfg.service_role_key}",
    }
    if extra:
        headers.update(extra)
    return headers


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def storage_path(*parts: str) -> str:
    cleaned = []
    for part in parts:
        text = str(part or "").strip().replace("\\", "/")
        text = "/".join(segment for segment in text.split("/") if segment and segment not in {".", ".."})
        if text:
            cleaned.append(text)
    return "/".join(cleaned)


def upload_file(local_path: Path, remote_path: str, *, content_type: str | None = None, upsert: bool = False) -> dict[str, Any]:
    cfg = get_config()
    if not cfg:
        return {"enabled": False, "uploaded": False, "reason": "Supabase no configurado"}
    content_type = content_type or mimetypes.guess_type(local_path.name)[0] or "application/octet-stream"
    url = f"{cfg.url}/storage/v1/object/{cfg.bucket}/{remote_path}"
    headers = _headers(cfg, {"Content-Type": content_type, "x-upsert": "true" if upsert else "false"})
    with httpx.Client(timeout=60) as client:
        with local_path.open("rb") as fh:
            res = client.post(url, headers=headers, content=fh)
            res.raise_for_status()
    return {
        "enabled": True,
        "uploaded": True,
        "bucket": cfg.bucket,
        "path": remote_path,
        "sha256": sha256_file(local_path),
        "size": local_path.stat().st_size,
    }


def download_file(remote_path: str, local_path: Path, *, timeout: int = 120) -> dict[str, Any]:
    cfg = get_config()
    if not cfg:
        return {"enabled": False, "downloaded": False, "reason": "Supabase no configurado"}
    url = f"{cfg.url}/storage/v1/object/{cfg.bucket}/{remote_path}"
    headers = _headers(cfg)
    local_path.parent.mkdir(parents=True, exist_ok=True)
    with httpx.Client(timeout=timeout) as client:
        with client.stream("GET", url, headers=headers) as res:
            res.raise_for_status()
            with local_path.open("wb") as fh:
                for chunk in res.iter_bytes():
                    fh.write(chunk)
    return {
        "enabled": True,
        "downloaded": True,
        "bucket": cfg.bucket,
        "path": remote_path,
        "local_path": str(local_path),
        "size": local_path.stat().st_size,
        "sha256": sha256_file(local_path),
    }


def create_signed_upload_url(remote_path: str, *, upsert: bool = False) -> dict[str, Any]:
    cfg = get_config()
    if not cfg:
        return {"enabled": False, "signed": False, "reason": "Supabase no configurado"}
    url = f"{cfg.url}/storage/v1/object/upload/sign/{cfg.bucket}/{remote_path}"
    headers = _headers(cfg, {"Content-Type": "application/json"})
    with httpx.Client(timeout=30) as client:
        res = client.post(url, headers=headers, json={"upsert": upsert})
        res.raise_for_status()
        data = res.json() if res.content else {}
    return {"enabled": True, "signed": True, "bucket": cfg.bucket, "path": remote_path, **data}


def select_rows(table: str, params: dict[str, str]) -> list[dict[str, Any]]:
    cfg = get_config()
    if not cfg:
        return []
    url = f"{cfg.url}/rest/v1/{table}"
    headers = _headers(cfg)
    with httpx.Client(timeout=30) as client:
        res = client.get(url, headers=headers, params=params)
        res.raise_for_status()
        return res.json() if res.content else []


def tenant_id() -> str | None:
    cfg = get_config()
    if not cfg:
        return None
    rows = select_rows("tenants", {"slug": f"eq.{cfg.tenant_slug}", "select": "id", "limit": "1"})
    if rows:
        return rows[0].get("id")
    created = insert_row("tenants", {"slug": cfg.tenant_slug, "nombre": "CCU Argentina - MVP"})
    data = created.get("data") or []
    return data[0].get("id") if data else None


def insert_row(table: str, payload: dict[str, Any]) -> dict[str, Any]:
    cfg = get_config()
    if not cfg:
        return {"enabled": False, "inserted": False, "reason": "Supabase no configurado"}
    url = f"{cfg.url}/rest/v1/{table}"
    headers = _headers(cfg, {"Content-Type": "application/json", "Prefer": "return=representation"})
    with httpx.Client(timeout=30) as client:
        res = client.post(url, headers=headers, json=payload)
        res.raise_for_status()
        data = res.json() if res.content else []
    return {"enabled": True, "inserted": True, "table": table, "data": data}


def insert_rows(table: str, payloads: list[dict[str, Any]], *, timeout: int = 120) -> dict[str, Any]:
    cfg = get_config()
    if not cfg:
        return {"enabled": False, "inserted": False, "reason": "Supabase no configurado"}
    if not payloads:
        return {"enabled": True, "inserted": True, "table": table, "count": 0}
    url = f"{cfg.url}/rest/v1/{table}"
    headers = _headers(cfg, {"Content-Type": "application/json", "Prefer": "return=minimal"})
    with httpx.Client(timeout=timeout) as client:
        res = client.post(url, headers=headers, json=payloads)
        res.raise_for_status()
    return {"enabled": True, "inserted": True, "table": table, "count": len(payloads)}


def update_rows(table: str, filters: dict[str, str], payload: dict[str, Any], *, timeout: int = 30) -> dict[str, Any]:
    cfg = get_config()
    if not cfg:
        return {"enabled": False, "updated": False, "reason": "Supabase no configurado"}
    url = f"{cfg.url}/rest/v1/{table}"
    headers = _headers(cfg, {"Content-Type": "application/json", "Prefer": "return=minimal"})
    with httpx.Client(timeout=timeout) as client:
        res = client.patch(url, headers=headers, params=filters, json=payload)
        res.raise_for_status()
    return {"enabled": True, "updated": True, "table": table}


def _padron_job_select() -> str:
    return (
        "id,tenant_id,provincia,periodo,vigencia_hasta,fuente_id,cliente,cuit_agente,estado,"
        "storage_original_path,storage_normalizado_path,archivo_nombre,tamano_bytes,sha256_original,"
        "sha256_normalizado,registros_raw,registros_validos,registros_insertados,errores,"
        "advertencias,calidad,job_metadata,cloud_run_execution,creado_en,actualizado_en,iniciado_en,finalizado_en"
    )


def create_padron_import_job(
    *,
    provincia: str,
    archivo_nombre: str,
    periodo: str = "",
    vigencia_hasta: str | None = None,
    fuente_id: str = "",
    cliente: str = "CCU",
    cuit_agente: str = "",
    tamano_bytes: int = 0,
) -> dict[str, Any]:
    cfg = get_config()
    tid = tenant_id()
    if not cfg or not tid:
        return {"enabled": False, "created": False, "reason": "Supabase no configurado"}
    job_id = str(uuid.uuid4())
    periodo_path = periodo or "sin-periodo"
    remote = storage_path(cfg.tenant_slug, "padrones", provincia, periodo_path, "original", job_id, archivo_nombre)
    payload = {
        "id": job_id,
        "tenant_id": tid,
        "provincia": provincia,
        "periodo": periodo or "",
        "vigencia_hasta": vigencia_hasta or None,
        "fuente_id": fuente_id or None,
        "cliente": cliente or "CCU",
        "cuit_agente": cuit_agente or "",
        "estado": "pendiente_upload",
        "storage_original_path": remote,
        "archivo_nombre": archivo_nombre,
        "tamano_bytes": int(tamano_bytes or 0),
        "job_metadata": {"pipeline": "cloud_run_jobs", "upload": "supabase_storage"},
    }
    inserted = insert_row(PADRON_IMPORT_TABLE, payload)
    data = (inserted.get("data") or [payload])[0]
    signed = create_signed_upload_url(remote)
    return {"enabled": True, "created": True, "job": data, "upload": signed}


def get_padron_import_job(job_id: str) -> dict[str, Any] | None:
    tid = tenant_id()
    if not tid:
        return None
    rows = select_rows(PADRON_IMPORT_TABLE, {
        "select": _padron_job_select(),
        "tenant_id": f"eq.{tid}",
        "id": f"eq.{job_id}",
        "limit": "1",
    })
    return rows[0] if rows else None


def list_padron_import_jobs(*, limit: int = 20, estado: str = "") -> list[dict[str, Any]]:
    tid = tenant_id()
    if not tid:
        return []
    params = {
        "select": _padron_job_select(),
        "tenant_id": f"eq.{tid}",
        "order": "creado_en.desc",
        "limit": str(max(1, min(limit, 100))),
    }
    if estado:
        params["estado"] = f"eq.{estado}"
    return select_rows(PADRON_IMPORT_TABLE, params)


def update_padron_import_job(job_id: str, patch: dict[str, Any]) -> dict[str, Any]:
    tid = tenant_id()
    if not tid:
        return {"enabled": False, "updated": False, "reason": "Supabase no configurado"}
    payload = dict(patch)
    payload["actualizado_en"] = datetime.now(timezone.utc).isoformat()
    return update_rows(PADRON_IMPORT_TABLE, {"tenant_id": f"eq.{tid}", "id": f"eq.{job_id}"}, payload)


def buscar_padron_registro(cuit_limpio: str, provincia: str) -> dict[str, Any] | None:
    tid = tenant_id()
    if not tid:
        return None
    rows = select_rows("padron_registros_demo", {
        "select": "cuit,jurisdiccion,regimen,alicuota_retencion,alicuota_percepcion,vigencia_desde,vigencia_hasta,datos",
        "tenant_id": f"eq.{tid}",
        "cuit": f"eq.{cuit_limpio}",
        "jurisdiccion": f"eq.{provincia}",
        "limit": "1",
    })
    if not rows:
        return None
    row = rows[0]
    return {
        "encontrado": True,
        "alicuota_retencion": row.get("alicuota_retencion") or "—",
        "alicuota_percepcion": row.get("alicuota_percepcion") or "—",
        "vigencia_desde": row.get("vigencia_desde") or "",
        "vigencia_hasta": row.get("vigencia_hasta") or "",
        "regimen": row.get("regimen") or "",
        "fuente": "supabase",
    }


def provincia_tiene_padron_activo(provincia: str) -> bool:
    tid = tenant_id()
    if not tid:
        return False
    rows = select_rows("padron_versiones", {
        "select": "id",
        "tenant_id": f"eq.{tid}",
        "provincia": f"eq.{provincia}",
        "estado": "eq.activo",
        "limit": "1",
    })
    return bool(rows)


def sync_padron_importado(
    *,
    archivo_local: Path,
    provincia: str,
    resultado_importacion: dict[str, Any],
    cliente: str = "CCU",
    fuente_id: str = "",
) -> dict[str, Any]:
    """Sube original y registra metadata. Nunca debe romper el flujo local."""
    cfg = get_config()
    if not cfg:
        return {"enabled": False, "synced": False, "reason": "Supabase no configurado"}
    periodo = resultado_importacion.get("periodo") or "sin-periodo"
    remote = storage_path(cfg.tenant_slug, "padrones", provincia, periodo, "original", archivo_local.name)
    upload = upload_file(archivo_local, remote, upsert=False)
    tid = tenant_id()
    payload = {
        "tenant_id": tid,
        "provincia": provincia,
        "fuente_id": fuente_id or None,
        "periodo": resultado_importacion.get("periodo") or "",
        "vigencia_hasta": resultado_importacion.get("vigencia_hasta") or None,
        "registros": int(resultado_importacion.get("registros") or 0),
        "estado": "activo" if resultado_importacion.get("calidad", {}).get("estado") != "rechazado" else "rechazado",
        "storage_original_path": remote,
        "sha256_original": upload.get("sha256", ""),
        "calidad": resultado_importacion.get("calidad") or {},
        "evidencia": {"cliente": cliente, "upload": upload},
    }
    insert = insert_row("padron_versiones", payload)
    return {"enabled": True, "synced": True, "upload": upload, "insert": insert}


LEGAJOS_TABLE = "legajos"
_LEGAJO_CAMPOS = (
    "id", "creado_en", "estado", "operador", "excel", "total_proveedores",
    "sha256", "reglas_aplicadas", "padrones_snapshot", "resumen", "resultados",
)


def sync_legajo(legajo: dict[str, Any]) -> dict[str, Any]:
    """Persiste el legajo sellado en Supabase. Nunca debe romper el flujo local."""
    cfg = get_config()
    if not cfg:
        return {"enabled": False, "synced": False, "reason": "Supabase no configurado"}
    payload = {campo: legajo.get(campo) for campo in _LEGAJO_CAMPOS}
    payload["tenant_id"] = tenant_id()
    insert = insert_row(LEGAJOS_TABLE, payload)
    return {"enabled": True, "synced": True, "insert": {"inserted": insert.get("inserted", False)}}


def list_legajos_remotos(limit: int = 100) -> list[dict[str, Any]]:
    tid = tenant_id()
    if not tid:
        return []
    return select_rows(LEGAJOS_TABLE, {
        "select": "id,creado_en,estado,operador,excel,total_proveedores,sha256,resumen",
        "tenant_id": f"eq.{tid}",
        "order": "creado_en.desc",
        "limit": str(max(1, min(limit, 500))),
    })


def get_legajo_remoto(legajo_id: str) -> dict[str, Any] | None:
    tid = tenant_id()
    if not tid:
        return None
    rows = select_rows(LEGAJOS_TABLE, {
        "select": ",".join(_LEGAJO_CAMPOS),
        "tenant_id": f"eq.{tid}",
        "id": f"eq.{legajo_id}",
        "limit": "1",
    })
    return rows[0] if rows else None


def sync_acceso(acceso: dict[str, Any]) -> dict[str, Any]:
    if not get_config():
        return {"enabled": False, "synced": False, "reason": "Supabase no configurado"}
    tid = tenant_id()
    payload = {"tenant_id": tid}
    payload.update({k: acceso.get(k) for k in (
        "id", "cliente", "cuit_agente", "cuit_agente_limpio", "organismo", "servicio", "fuente_id",
        "tipo_acceso", "estado", "alcance", "responsable", "notas", "evidencias", "historial",
    )})
    insert = insert_row("accesos_fiscales", payload)
    return {"enabled": True, "synced": True, "insert": insert}
