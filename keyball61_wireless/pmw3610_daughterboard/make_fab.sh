#!/usr/bin/env bash
# End-to-end: place -> DSN -> Freerouting -> SES import -> pour+DRC -> gerbers.
set -euo pipefail
cd "$(dirname "$0")"

PY=/usr/bin/python3
FR="${FREEROUTING_JAR:?set FREEROUTING_JAR to the freerouting jar path}"
PCB=pmw3610_daughterboard.kicad_pcb
DSN=pmw3610_daughterboard.dsn
SES=pmw3610_daughterboard.ses
GERB=gerbers

echo "== 1. place + net =="
$PY build_board.py 2>&1 | grep -v "PROPERTY_ENUM\|m_choices" || true

echo "== 2. export Specctra DSN (via pcbnew) =="
$PY export_dsn.py "$PCB" "$DSN" 2>&1 | grep -v "PROPERTY_ENUM\|m_choices" || true
ls -la "$DSN"

echo "== 3. Freerouting (headless, auto-route) =="
java -Dgui.enabled=false -jar "$FR" -de "$DSN" -do "$SES" -mp 20 -mt 2 2>&1 \
  | grep -iE "pass|route|complet|error|incomplete|via|written|saved" | tail -25 || true
ls -la "$SES"

echo "== 4. import routed session back into the board =="
$PY import_ses.py "$PCB" "$SES" 2>&1 | grep -v "PROPERTY_ENUM\|m_choices" || true

echo "== 5. DRC =="
kicad-cli pcb drc --output drc.json --format json --severity-error "$PCB" 2>&1 \
  | grep -v "PROPERTY_ENUM\|m_choices" | tail -4 || true

echo "== 6. gerbers + drill =="
rm -rf "$GERB"; mkdir -p "$GERB"
kicad-cli pcb export gerbers --output "$GERB/" \
  --layers F.Cu,B.Cu,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts \
  --subtract-soldermask --no-protel-ext --check-zones "$PCB" \
  2>&1 | grep -v "PROPERTY_ENUM\|m_choices" | tail -12 || true
kicad-cli pcb export drill --output "$GERB/" --format excellon \
  --excellon-units mm --excellon-separate-th --drill-origin absolute \
  --generate-map --map-format gerberx2 "$PCB" \
  2>&1 | grep -v "PROPERTY_ENUM\|m_choices" | tail -6 || true
echo "== gerber files =="; ls -la "$GERB"
