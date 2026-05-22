#!/usr/bin/env bash
# Arranca el prototipo con uv (que ya tenés instalado en /Users/berna/.local/bin/uv)

set -e
cd "$(dirname "$0")"

# Copiar .env si no existe
if [ ! -f .env ]; then
  cp .env.example .env
  echo "Se creó .env desde .env.example. Editalo si querés activar modo live."
fi

echo ""
echo "==> Instalando dependencias (uv sync)..."
/Users/berna/.local/bin/uv sync

echo ""
echo "==> Arrancando servidor en http://localhost:8000"
echo "    (Ctrl+C para detener)"
echo ""

exec /Users/berna/.local/bin/uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
