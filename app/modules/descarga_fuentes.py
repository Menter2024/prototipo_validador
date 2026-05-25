"""Descarga controlada y evidencia de fuentes fiscales."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

import httpx

from app.modules import fuentes_catalogo

MANIFEST = "fuentes_descargas_manifest.json"
IMPORTABLE_EXTS = {".csv", ".txt", ".tsv", ".psv", ".xlsx", ".xlsm", ".zip"}


class _LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[dict] = []
        self._current: dict | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        href = dict(attrs).get("href")
        if href:
            self._current = {"href": href, "text": ""}

    def handle_data(self, data: str) -> None:
        if self._current is not None:
            self._current["text"] += data

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._current is not None:
            self.links.append(self._current)
            self._current = None


def _manifest_path(evidencias_dir: Path) -> Path:
    return evidencias_dir / MANIFEST


def cargar_manifest(evidencias_dir: Path) -> dict:
    path = _manifest_path(evidencias_dir)
    if not path.exists():
        return {"version": 1, "descargas": []}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"version": 1, "descargas": []}


def guardar_manifest(evidencias_dir: Path, manifest: dict) -> None:
    evidencias_dir.mkdir(parents=True, exist_ok=True)
    _manifest_path(evidencias_dir).write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def _fuente_por_id(fuente_id: str) -> dict:
    for fuente in fuentes_catalogo.cargar_catalogo()["fuentes"]:
        if fuente.get("id") == fuente_id:
            return fuente
    raise ValueError(f"Fuente no encontrada: {fuente_id}")


def _filename_from_url(url: str, fallback: str) -> str:
    name = Path(urlparse(url).path).name
    if not name or "." not in name:
        return fallback
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name)


def _candidate_links(html: str, landing_url: str, cfg: dict) -> list[dict]:
    parser = _LinkParser()
    parser.feed(html)
    text_re = re.compile(cfg.get("link_text_regex", ".*"), re.I)
    exts = tuple(e.lower() for e in cfg.get("extensiones", []))
    candidates = []
    for link in parser.links:
        text = " ".join(link.get("text", "").split())
        url = urljoin(landing_url, link["href"])
        path = urlparse(url).path.lower()
        if text_re.search(text) and (not exts or path.endswith(exts)):
            candidates.append({"url": url, "text": text, "extension": Path(path).suffix.lower()})
    return candidates


def plan_descarga(fuente_id: str) -> dict:
    fuente = _fuente_por_id(fuente_id)
    descarga = fuente.get("descarga") or {}
    modo = descarga.get("modo", "sin_descarga_configurada")
    base = {
        "fuente_id": fuente_id,
        "nombre": fuente.get("nombre"),
        "modo": modo,
        "descargable": modo == "pagina_publica_links",
        "landing_url": descarga.get("landing_url") or fuente.get("url"),
        "nota": descarga.get("nota", ""),
    }
    if modo == "requiere_credenciales":
        return {
            **base,
            "status": "requiere_credenciales",
            "detalle": f"Requiere {descarga.get('credencial', 'credenciales')} para automatizar descarga.",
        }
    if modo == "monitoreo_publicacion":
        return {
            **base,
            "status": "monitoreo_publicacion",
            "detalle": "Requiere monitorear publicación normativa o cargar archivo oficial exportado.",
        }
    if modo != "pagina_publica_links":
        return {**base, "status": "sin_descarga_configurada", "detalle": "No hay estrategia de descarga automática definida."}
    return {**base, "status": "lista_para_relevar", "detalle": "Se buscará el enlace vigente en la página pública."}


def ejecutar_descarga(fuente_id: str, evidencias_dir: Path, dry_run: bool = True, timeout: float = 20.0) -> dict:
    fuente = _fuente_por_id(fuente_id)
    descarga = fuente.get("descarga") or {}
    plan = plan_descarga(fuente_id)
    if plan["status"] != "lista_para_relevar":
        resultado = {**plan, "ok": False, "dry_run": dry_run}
        _registrar(evidencias_dir, resultado)
        return resultado

    landing_url = descarga["landing_url"]
    with httpx.Client(timeout=timeout, follow_redirects=True) as client:
        page = client.get(landing_url)
        page.raise_for_status()
        candidates = _candidate_links(page.text, str(page.url), descarga)
        if not candidates:
            resultado = {
                **plan,
                "ok": False,
                "dry_run": dry_run,
                "status": "sin_candidatos",
                "detalle": "No se encontraron enlaces compatibles en la página pública.",
            }
            _registrar(evidencias_dir, resultado)
            return resultado
        selected = candidates[0]
        if dry_run:
            resultado = {
                **plan,
                "ok": True,
                "dry_run": True,
                "status": "candidato_detectado",
                "candidato": selected,
                "candidatos": candidates[:10],
            }
            _registrar(evidencias_dir, resultado)
            return resultado

        artifact = client.get(selected["url"])
        artifact.raise_for_status()
        fuente_dir = evidencias_dir / fuente_id
        fuente_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = _filename_from_url(selected["url"], f"{fuente_id}_{ts}.bin")
        destino = fuente_dir / f"{ts}_{filename}"
        destino.write_bytes(artifact.content)
        sha256 = hashlib.sha256(artifact.content).hexdigest()
        ext = destino.suffix.lower()
        resultado = {
            **plan,
            "ok": True,
            "dry_run": False,
            "status": "descargado",
            "candidato": selected,
            "archivo": str(destino),
            "bytes": len(artifact.content),
            "sha256": sha256,
            "content_type": artifact.headers.get("content-type", ""),
            "importable": ext in IMPORTABLE_EXTS,
            "detalle": "Archivo descargado y evidenciado; importar si el formato es soportado.",
        }
        if ext == ".rar":
            resultado["detalle"] = "Archivo RAR descargado y evidenciado; requiere extracción externa antes de importar."
            resultado["importable"] = False
        _registrar(evidencias_dir, resultado)
        return resultado


def _registrar(evidencias_dir: Path, resultado: dict) -> None:
    manifest = cargar_manifest(evidencias_dir)
    item = {"fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), **resultado}
    manifest.setdefault("descargas", []).insert(0, item)
    manifest["descargas"] = manifest["descargas"][:100]
    guardar_manifest(evidencias_dir, manifest)
