@echo off
REM ============================================================
REM  SportsField — Install ^& Start (Windows)
REM ============================================================

cd /d "%~dp0"

echo =====================================
echo   SportsField — Setup ^& Launch
echo =====================================
echo.

REM ── 1. Create virtual environment if missing ───────────────
if not exist "venv" (
    echo [1/5] Creating virtual environment...
    python -m venv venv
) else (
    echo [1/5] Virtual environment already exists.
)

REM ── 2. Activate virtual environment ────────────────────────
echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat

REM ── 3. Install dependencies ────────────────────────────────
echo [3/5] Installing requirements...
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

REM ── 4. Initialize / migrate database ───────────────────────
if not exist "migrations\versions" (
    echo [4/5] Initializing database...
    flask db init 2>nul
    flask db migrate -m "Initial migration" 2>nul
    flask db upgrade
) else (
    echo [4/5] Running database migrations...
    flask db upgrade
)

REM ── 5. Create default admin user ───────────────────────────
echo [5/5] Seeding admin user...
python create_admin.py

echo.
echo =====================================
echo   Server starting on http://127.0.0.1:5000
echo   Press Ctrl+C to stop
echo =====================================
echo.

REM ── Start Flask dev server ─────────────────────────────────
python run.py

pause
