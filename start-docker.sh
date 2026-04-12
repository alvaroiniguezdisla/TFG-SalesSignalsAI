#!/bin/bash
# ==============================================================
# SalesSignalsAI - Script de Arranque Docker
# Uso: chmod +x start-docker.sh && ./start-docker.sh
# Este script delega en docker compose para evitar stacks duplicados.
# ==============================================================
set -euo pipefail

export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 SalesSignalsAI - Arrancando con Docker Compose..."

# Limpiamos posibles contenedores antiguos creados por versiones previas del script
docker stop ssai-backend ssai-frontend 2>/dev/null || true
docker rm ssai-backend ssai-frontend 2>/dev/null || true
docker network rm ssai-net 2>/dev/null || true

echo "🧹 Limpiando stack previo de Compose..."
docker compose down --remove-orphans || true

echo "📦 Construyendo y arrancando servicios..."
docker compose up --build -d

echo ""
echo "✅ ¡Todo listo!"
docker compose ps
echo ""
echo "   Backend:  http://localhost:8000"
echo "   Frontend: http://localhost:5173"
echo ""
echo "Logs:      docker compose logs -f"
echo "Para parar: docker compose down"
