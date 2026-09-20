#!/usr/bin/env bash
# ============================================================
#  SportsField — Install & Start (Linux / macOS)
# ============================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "====================================="
echo "  SportsField — Setup & Launch"
echo "====================================="
echo ""

# ── 1. Create virtual environment if missing ─────────────────
if [ ! -d "venv" ]; then
    echo "[1/5] Creating virtual environment..."
    python3 -m venv venv
else
    echo "[1/5] Virtual environment already exists."
fi

# ── 2. Activate virtual environment ──────────────────────────
echo "[2/5] Activating virtual environment..."
source venv/bin/activate

# ── 3. Install dependencies ─────────────────────────────────
echo "[3/5] Installing requirements..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

# ── 4. Initialize / migrate database ────────────────────────
if [ ! -d "migrations/versions" ] || [ -z "$(ls -A migrations/versions 2>/dev/null)" ]; then
    echo "[4/5] Initializing database..."
    flask db init 2>/dev/null || true
    flask db migrate -m "Initial migration" 2>/dev/null || true
    flask db upgrade
else
    echo "[4/5] Running database migrations..."
    flask db upgrade
fi

# ── 5. Create default admin user ─────────────────────────────
echo "[5/5] Seeding admin user..."
python create_admin.py

echo ""
echo "====================================="
echo "  Server starting on http://127.0.0.1:5000"
echo "  Press Ctrl+C to stop"
echo "====================================="
echo ""

# ── Start Flask dev server ───────────────────────────────────
python run.py
