#!/usr/bin/env bash
# Launch The Unofficial Guide. Builds the index on first run, then starts the web app.
# Usage:  ./run.sh           (build if needed, then launch the UI)
#         ./run.sh build     (force-rebuild the index only)
#         ./run.sh eval      (run the 5-question evaluation instead of the UI)
set -e
cd "$(dirname "$0")"

PY=".venv/bin/python"

# 1. Make sure the virtual environment + dependencies exist.
if [ ! -x "$PY" ]; then
  echo "==> Creating virtual environment (.venv) and installing dependencies..."
  python3 -m venv .venv
  .venv/bin/pip install --upgrade pip -q
  .venv/bin/pip install -r requirements.txt
fi

# 2. Make sure a Groq API key is set.
if [ ! -f .env ] || grep -q "your_key_here" .env; then
  echo "!! No Groq API key found. Copy .env.example to .env and add your key,"
  echo "   get a free one at https://console.groq.com"
  exit 1
fi

# 3. Build the index if it's missing (or if 'build' was requested).
if [ "$1" = "build" ] || [ ! -d chroma_db ]; then
  echo "==> Building chunks and vector index..."
  $PY -m src.build_chunks
  $PY -m src.vectorstore --build
  [ "$1" = "build" ] && exit 0
fi

# 4. Run.
if [ "$1" = "eval" ]; then
  $PY -m src.evaluate
else
  echo "==> Starting the web app at http://localhost:7860 (Ctrl+C to stop)"
  $PY app.py
fi
