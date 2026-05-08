#!/bin/bash
# SessionStart-Hook für RagVenture
# Installiert Python-Abhängigkeiten und das spaCy-Modell, damit Linter
# und Tests in Claude Code on the Web direkt funktionieren.

set -euo pipefail

# Nur in der Remote-Umgebung ausführen (lokales venv soll unangetastet bleiben)
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-$(pwd)}"

# Damit `from controller...` & Co. funktionieren (Imports liegen in src/)
echo 'export PYTHONPATH="${CLAUDE_PROJECT_DIR}/src:${PYTHONPATH:-}"' >> "$CLAUDE_ENV_FILE"

python3 -m pip install -r requirements.txt

# spaCy-Modell für deutschen Parser
python3 -m spacy download de_dep_news_trf
