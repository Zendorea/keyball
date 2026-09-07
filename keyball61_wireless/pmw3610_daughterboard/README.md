# PMW3610 Trackball Daughterboard — Keyball61 Wireless

Drop-in replacement for the stock Keyball61 PMW3360 ball-reader board, redesigned
for the low-power **PMW3610** sensor on a **nice!nano / ZMK** wireless build.
Keeps the stock Keyball **7-pin** connector at the exact original positions (drops
into a stock Keyball main board) and adds a **separate MOTION solder hole** so ZMK
can run the sensor interrupt-driven for best battery life.

**Status: final, DRC-clean, gerbers ordered from PCBway.**

## Board summary
- **23.0 × 25.0 mm**, 2-layer, **1.0 mm**, ENIG. U-shaped outline with a lens slot
  open to the top edge, sized to the **LM18-LSI** lens body.
- **PMW3610 optical center** at the original ball-facing position; connector +
  sensor share the X=11.0 mm centerline (ball centers on the IC via the stock
  Keyball cage).
- **7-pin connector** (CK·IO·G·V·G·CS·RST) at exact stock 2.54 mm positions +
  a separate **MOT** solder hole on the same pitch.
- Full PMW3610 support: **TLV74318** 1.8 V LDO + charge-pump/decoupling caps +
  NRESET & MOTION pull-ups. Solid B.Cu GND pour with stitching vias.
- DRC: **0 unrouted / 0 unconnected / 0 electrical / 0 hole-clearance**
  (5 non-fatal courtyard-overlap advisories — not fab-blocking).

## Files
| File | What it is |
|------|-----------|
| `DESIGN.md` | Full design spec: optics Z-stack, connector, MOTION, datasheet notes. |
| `BOM.csv` | As-built bill of materials with LCSC part numbers + cap-to-pin mapping. |
| `pmw3610_daughterboard.kicad_pcb` / `.kicad_pro` | Final routed board + project. |
| `pmw3610_daughterboard.kicad_dru` | Custom design rules (0.15 mm edge clearance). |
| `pmw3610_kb.pretty/` | The 3 custom footprints used: PMW3610 (siderakb), 7-pin connector, MOTION pad. |
| `fp-lib-table` | Resolves the local footprint lib on open. |
| `gerbers/` + `pmw3610_daughterboard_gerbers.zip` | Fab package (PCBway-ready): 7 gerbers + separate PTH/NPTH Excellon drills. |
| `drc.json` | Latest DRC report. |
| `board_final.png` / `board_top.png` / `board_bot.png` | Renders. |

## Reproducible build pipeline (KiCad 10 pcbnew + Freerouting 2.4.1)
Run in order (system `python3` with `pcbnew`, except footprints which use kiutils):
```
make_footprints_v2.py   -> custom footprints (sensor, 7-pin conn, MOTION pad)
build_board_22x25.py    -> place + net + design rules
export_dsn.py           -> Specctra DSN
Freerouting (headless, -mt 1, --router.via_costs=30, -inc GND)
import_ses.py           -> import routed session
pour_gnd.py             -> B.Cu GND pour (solid pad connection)
finish_22x25.py         -> GND stitching vias; fill zones last
kicad-cli pcb drc / export gerbers,drill
```

## Parts sourcing
- **Sensor + lens:** PMW3610DM-**SUDU** + **LM18-LSI** as a SET on AliExpress
  (not stocked at LCSC/Digikey). Match the lens (LM18-LSI) — avoid the 3360/LM19.
- **Passives + LDO + header:** LCSC (see `BOM.csv` for exact part numbers).
- **Ball:** 34 mm (Perixx PERIPRO-303 / SANWA).

## Firmware
Wireless ZMK config lives in a separate repo (`zmk-config-keyball61-wireless`):
trackball on `&spi1` — SCK P1.13, SDIO P0.10 (3-wire), CS P0.09, MOTION P1.11,
2 MHz. See that repo's README.

## Verify before assembly
- Sensor/lens standoff vs your trackball housing (base-plate sets focus, not PCB thickness).
- Continuity-check the sensor pins (esp. SCLK) after soldering — the most common DIY failure.
