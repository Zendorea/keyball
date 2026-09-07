#!/usr/bin/env bash
# Corrected flow (per KiCad+Freerouting best practice):
#  place (NO pour) -> DSN -> Freerouting (-mt 1, ignore GND) -> import SES ->
#  pour+fill GND (island-aware, after routing) -> DRC (with .kicad_dru edge rule)
#  -> gerbers. Edge clearance persists via pmw3610_daughterboard.kicad_dru.
set -euo pipefail
cd "$(dirname "$0")"

PY=/usr/bin/python3
KPY="${KIUTILS_PY:-$KIROCREW_SCRATCH/kicadenv/bin/python}"
FR="${FREEROUTING_JAR:?set FREEROUTING_JAR}"
PCB=pmw3610_daughterboard.kicad_pcb
DSN=pmw3610_daughterboard.dsn
SES=pmw3610_daughterboard.ses
GERB=gerbers

echo "== 0. footprints =="
$KPY make_footprints_v2.py 2>&1 | grep -v "PROPERTY_ENUM\|m_choices" || true

echo "== 1. place + net (v3, 22x25 + slot, NO pour) =="
$PY build_board_v3.py 2>&1 | grep -v "PROPERTY_ENUM\|m_choices" || true

echo "== 2. export Specctra DSN =="
$PY export_dsn.py "$PCB" "$DSN" 2>&1 | grep -v "PROPERTY_ENUM\|m_choices" || true

echo "== 3. Freerouting (headless, single-thread, ignore GND, cheap vias) =="
java -Dgui.enabled=false -jar "$FR" -de "$DSN" -do "$SES" \
  -mp 100 -mt 1 -oit 0.1 -inc GND --router.via_costs=30 2>&1 \
  | grep -iE "unrouted and|Fanout stage|written|saved" | tail -8 || true

echo "== 4. import routed SES =="
$PY import_ses.py "$PCB" "$SES" 2>&1 | grep -v "PROPERTY_ENUM\|m_choices" || true

echo "== 5. pour + fill GND (post-route) + widen thin tracks =="
$PY pour_and_fill.py "$PCB" 2>&1 | grep -v "PROPERTY_ENUM\|m_choices" || true

echo "== 6. DRC (honours .kicad_dru edge rule) =="
kicad-cli pcb drc --output drc.json --format json --severity-error "$PCB" 2>&1 \
  | grep -v "PROPERTY_ENUM\|m_choices" | tail -3 || true

echo "== 7. gerbers + drill =="
rm -rf "$GERB"; mkdir -p "$GERB"
kicad-cli pcb export gerbers --output "$GERB/" \
  --layers F.Cu,B.Cu,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts \
  --subtract-soldermask --no-protel-ext --check-zones "$PCB" \
  2>&1 | grep -v "PROPERTY_ENUM\|m_choices" | grep -c Plotted || true
kicad-cli pcb export drill --output "$GERB/" --format excellon \
  --excellon-units mm --excellon-separate-th --drill-origin absolute \
  --generate-map --map-format gerberx2 "$PCB" \
  2>&1 | grep -v "PROPERTY_ENUM\|m_choices" | grep -c "Created file" || true
