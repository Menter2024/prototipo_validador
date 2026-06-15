#!/usr/bin/env python3
"""Guardrail para exigir revisión DOX/docs/tests en cambios críticos."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


CRITICAL_PREFIXES = (
    "app/",
    "config/",
    "padrones/",
    "scripts/",
    "supabase/",
)
IGNORED_PREFIXES = (
    ".git/",
    ".pytest_cache/",
    "salidas/",
    "uploads/",
)


def _run_git(repo: Path, args: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _normalize(path: str) -> str:
    return path.replace("\\", "/").lstrip("./")


def collect_changed_files(repo: Path, mode: str, base: str | None) -> list[str]:
    if mode == "staged":
        files = _run_git(repo, ["diff", "--cached", "--name-only", "--diff-filter=ACMR"])
    elif mode == "workspace":
        files = _run_git(repo, ["diff", "--name-only", "--diff-filter=ACMR", "HEAD"])
        files += _run_git(repo, ["ls-files", "--others", "--exclude-standard"])
    else:
        if not base:
            raise ValueError("--base is required when --mode=base")
        files = _run_git(repo, ["diff", "--name-only", "--diff-filter=ACMR", f"{base}...HEAD"])
    return sorted({_normalize(path) for path in files})


def is_ignored(path: str) -> bool:
    return path.endswith("/") or path.startswith(IGNORED_PREFIXES)


def is_agents(path: str) -> bool:
    return path == "AGENTS.md" or path.endswith("/AGENTS.md")


def is_doc(path: str) -> bool:
    return path == "README.md" or path.startswith("docs/") or is_agents(path)


def is_test(path: str) -> bool:
    return path.startswith("tests/") and not path.endswith("/AGENTS.md")


def is_critical(path: str) -> bool:
    return path.startswith(CRITICAL_PREFIXES) and not is_doc(path) and not is_test(path)


def dox_chain_for(path: str) -> set[str]:
    parts = Path(path).parts[:-1]
    chain = {"AGENTS.md"}
    current = Path()
    for part in parts:
        current /= part
        chain.add(_normalize(str(current / "AGENTS.md")))
    return chain


def evaluate_dox_guard(changed_files: list[str]) -> list[str]:
    files = sorted({_normalize(path) for path in changed_files if not is_ignored(_normalize(path))})
    docs_or_tests = {path for path in files if is_doc(path) or is_test(path)}
    findings: list[str] = []

    for path in files:
        if not is_critical(path):
            continue
        allowed_review = docs_or_tests | dox_chain_for(path)
        if not (set(files) & allowed_review):
            findings.append(
                f"{path}: falta actualizar/revisar docs, tests o AGENTS.md aplicable "
                f"({', '.join(sorted(dox_chain_for(path)))})"
            )

    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verifica que cambios críticos incluyan revisión DOX/docs/tests."
    )
    parser.add_argument("--repo", default=".", help="Ruta del repositorio.")
    parser.add_argument(
        "--mode",
        choices=("staged", "workspace", "base"),
        default="staged",
        help="Conjunto a revisar. Default: staged.",
    )
    parser.add_argument("--base", help="Base git para --mode=base, ej. origin/main.")
    args = parser.parse_args(argv)

    repo = Path(args.repo).resolve()
    changed_files = collect_changed_files(repo, args.mode, args.base)
    findings = evaluate_dox_guard(changed_files)

    if findings:
        print("DOX guard falló:", file=sys.stderr)
        for finding in findings:
            print(f"- {finding}", file=sys.stderr)
        return 1

    print("DOX guard OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

