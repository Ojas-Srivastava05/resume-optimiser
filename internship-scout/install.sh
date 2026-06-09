#!/usr/bin/env bash
set -euo pipefail

SCOUT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCOUT_DIR"

echo "→ Setting up Internship Scout in $SCOUT_DIR"

python3 -m venv venv
./venv/bin/pip install -q -r requirements.txt

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "→ Created .env — add your Gmail app password before the first email run."
fi

mkdir -p logs

PLIST_SRC="$SCOUT_DIR/com.ojas.internship-scout.plist"
PLIST_DST="$HOME/Library/LaunchAgents/com.ojas.internship-scout.plist"
sed "s|__SCOUT_DIR__|$SCOUT_DIR|g" "$PLIST_SRC" > "$PLIST_DST"

launchctl bootout "gui/$(id -u)/com.ojas.internship-scout" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST_DST"
launchctl enable "gui/$(id -u)/com.ojas.internship-scout"

echo ""
echo "✓ Installed. Daily run scheduled for 8:00 AM (your Mac's local timezone)."
echo "  Test now:  cd \"$SCOUT_DIR\" && ./venv/bin/python scout.py --dry-run"
echo "  First email: ./venv/bin/python scout.py --full   (after SMTP_APP_PASSWORD is set in .env)"
