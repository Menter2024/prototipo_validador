"""Automatización auditada de portales oficiales con Playwright.

No elude CAPTCHA, MFA ni controles de acceso. Los adaptadores autenticados
requieren autorización explícita y storage_state/credenciales fuera del repo.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).parent.parent.parent
DEFAULT_ADAPTERS = ROOT_DIR / "config" / "portal_adapters.json"
DEFAULT_OUTPUT_DIR = ROOT_DIR / "padrones" / "originales" / "portal"


class PortalAutomationError(RuntimeError):
    pass


def cargar_adapters(path: Path | None = None) -> dict[str, Any]:
    adapters_path = path or Path(os.environ.get("PORTAL_ADAPTERS", DEFAULT_ADAPTERS))
    data = json.loads(adapters_path.read_text(encoding="utf-8"))
    data.setdefault("adapters", [])
    return data


def adapter_por_id(adapter_id: str, path: Path | None = None) -> dict[str, Any]:
    for adapter in cargar_adapters(path)["adapters"]:
        if adapter.get("id") == adapter_id:
            return adapter
    raise PortalAutomationError(f"Adaptador no encontrado: {adapter_id}")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _render(valor: Any, variables: dict[str, Any]) -> Any:
    if isinstance(valor, str):
        return valor.format(**variables)
    if isinstance(valor, list):
        return [_render(v, variables) for v in valor]
    if isinstance(valor, dict):
        return {k: _render(v, variables) for k, v in valor.items()}
    return valor


def _variables(adapter: dict[str, Any], variables: dict[str, Any] | None) -> dict[str, Any]:
    merged = {"url": adapter.get("url", "")}
    merged.update(variables or {})
    periodo = merged.get("periodo")
    if periodo and "periodo_slash" not in merged:
        merged["periodo_slash"] = str(periodo).replace("-", "/")
    faltantes = [v for v in adapter.get("variables_requeridas", []) if not merged.get(v)]
    if faltantes:
        raise PortalAutomationError(f"Faltan variables requeridas para {adapter.get('id')}: {', '.join(faltantes)}")
    return merged


def validar_ejecucion(
    adapter: dict[str, Any],
    allow_authenticated: bool = False,
    allow_captcha: bool = False,
) -> tuple[bool, str]:
    if adapter.get("requiere_captcha") and not allow_captcha:
        return False, "Fuente con CAPTCHA: requiere cola asistida; no se automatiza resolución."
    if adapter.get("requiere_login") and not allow_authenticated:
        return False, "Fuente autenticada: requiere autorización explícita, storage_state o login asistido."
    return True, "ejecutable"


def plan_ejecucion(adapter_id: str, variables: dict[str, Any] | None = None, adapters_path: Path | None = None) -> dict[str, Any]:
    adapter = adapter_por_id(adapter_id, adapters_path)
    vars_render = _variables(adapter, variables)
    return {
        "adapter_id": adapter["id"],
        "fuente_id": adapter.get("fuente_id"),
        "nombre": adapter.get("nombre"),
        "tipo": adapter.get("tipo"),
        "url": adapter.get("url"),
        "requiere_login": adapter.get("requiere_login", False),
        "requiere_captcha": adapter.get("requiere_captcha", False),
        "acciones": [_render(a, vars_render) for a in adapter.get("acciones", [])],
        "evidencia": adapter.get("evidencia", []),
        "nota": adapter.get("nota", ""),
    }


def ejecutar_adapter(
    adapter_id: str,
    variables: dict[str, Any] | None = None,
    adapters_path: Path | None = None,
    output_dir: Path | None = None,
    headless: bool = True,
    allow_authenticated: bool = False,
    allow_captcha: bool = False,
    storage_state_path: Path | None = None,
    timeout_ms: int = 60_000,
    dry_run: bool = False,
) -> dict[str, Any]:
    adapter = adapter_por_id(adapter_id, adapters_path)
    vars_render = _variables(adapter, variables)
    permitido, razon = validar_ejecucion(adapter, allow_authenticated, allow_captcha)
    if dry_run:
        plan = plan_ejecucion(adapter_id, variables, adapters_path)
        plan["ejecutable"] = permitido
        plan["razon"] = razon
        return plan
    if not permitido:
        raise PortalAutomationError(razon)

    try:
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise PortalAutomationError(
            "Playwright no está instalado. Ejecutá: .venv/bin/python3.13 -m pip install playwright "
            "y luego .venv/bin/python3.13 -m playwright install chromium"
        ) from exc

    started = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_dir = Path(output_dir or DEFAULT_OUTPUT_DIR) / adapter_id / run_id
    downloads_dir = base_dir / "downloads"
    screenshots_dir = base_dir / "screenshots"
    html_dir = base_dir / "html"
    for d in (downloads_dir, screenshots_dir, html_dir):
        d.mkdir(parents=True, exist_ok=True)

    evidencia: dict[str, Any] = {
        "adapter_id": adapter_id,
        "fuente_id": adapter.get("fuente_id"),
        "nombre": adapter.get("nombre"),
        "tipo": adapter.get("tipo"),
        "url": adapter.get("url"),
        "started_at": started,
        "output_dir": str(base_dir),
        "downloaded_files": [],
        "screenshots": [],
        "html_files": [],
        "trace": "",
        "status": "iniciado",
        "error": "",
    }

    browser = context = None
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless, downloads_path=str(downloads_dir))
            context_args: dict[str, Any] = {"accept_downloads": True}
            if storage_state_path:
                context_args["storage_state"] = str(storage_state_path)
            context = browser.new_context(**context_args)
            context.set_default_timeout(timeout_ms)
            context.tracing.start(screenshots=True, snapshots=True, sources=True)
            page = context.new_page()

            for action_raw in adapter.get("acciones", []):
                action = _render(action_raw, vars_render)
                kind = action.get("type")
                if kind == "goto":
                    page.goto(action["url"], wait_until=action.get("wait_until", "load"))
                elif kind == "fill":
                    page.locator(action["selector"]).fill(str(action.get("value", "")))
                elif kind == "click":
                    page.locator(action["selector"]).click()
                elif kind == "wait_for_selector":
                    page.locator(action["selector"]).wait_for()
                elif kind == "click_download":
                    with page.expect_download() as download_info:
                        page.locator(action["selector"]).click()
                    download = download_info.value
                    filename = action.get("filename") or download.suggested_filename
                    destino = downloads_dir / filename
                    download.save_as(destino)
                    evidencia["downloaded_files"].append({
                        "path": str(destino),
                        "filename": destino.name,
                        "sha256": _sha256(destino),
                        "bytes": destino.stat().st_size,
                        "url": download.url,
                    })
                elif kind == "screenshot":
                    destino = screenshots_dir / action.get("filename", f"{len(evidencia['screenshots']) + 1}.png")
                    page.screenshot(path=destino, full_page=True)
                    evidencia["screenshots"].append(str(destino))
                elif kind == "save_html":
                    destino = html_dir / action.get("filename", f"{len(evidencia['html_files']) + 1}.html")
                    destino.write_text(page.content(), encoding="utf-8")
                    evidencia["html_files"].append(str(destino))
                else:
                    raise PortalAutomationError(f"Acción no soportada: {kind}")

            final_html = html_dir / "final.html"
            if not final_html.exists():
                final_html.write_text(page.content(), encoding="utf-8")
                evidencia["html_files"].append(str(final_html))
            trace_path = base_dir / "trace.zip"
            context.tracing.stop(path=trace_path)
            evidencia["trace"] = str(trace_path)
            evidencia["status"] = "ok"
    except PlaywrightTimeoutError as exc:
        evidencia["status"] = "timeout"
        evidencia["error"] = str(exc)
        raise PortalAutomationError(f"Timeout ejecutando {adapter_id}: {exc}") from exc
    except Exception as exc:
        evidencia["status"] = "error"
        evidencia["error"] = str(exc)
        raise
    finally:
        evidencia["finished_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        (base_dir / "evidencia.json").write_text(json.dumps(evidencia, ensure_ascii=False, indent=2), encoding="utf-8")
        if context:
            try:
                context.close()
            except Exception:
                pass
        if browser:
            try:
                browser.close()
            except Exception:
                pass
    return evidencia
