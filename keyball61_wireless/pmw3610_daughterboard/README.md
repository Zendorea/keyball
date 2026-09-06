# PMW3610 Trackball Daughterboard — Keyball61 Wireless

Drop-in replacement for the stock Keyball61 PMW3360 ball-reader board, redesigned
for the low-power **PMW3610** sensor on a **nice!nano / ZMK** wireless build. Adds
a **MOTION** interrupt line (8-pin connector vs the stock 7-pin) so ZMK runs the
sensor interrupt-driven for best battery life.

## Files
| File | What it is |
|------|-----------|
| `DESIGN.md` | Full design spec: sensor, BOM, verified pinout, ZMK config, mechanical. |
| `SCHEMATIC.md` | **Human-readable schematic** — block diagram + net-by-net connection list (source of truth). |
| `pmw3610_daughterboard.net` | KiCad netlist — import to reproduce connectivity / update PCB from schematic. |
| `pmw3610_daughterboard.kicad_pcb` | Placed + net-assigned board (24×32 mm, 2-layer). **Not yet routed.** |
| `pmw3610_daughterboard.kicad_pro` | KiCad project file. |
| `pmw3610_kb.pretty/` | Custom footprints: PMW3610 16-DIP, 8-pin Keyball connector. |
| `fp-lib-table` | Resolves the local footprint lib on open. |
| `make_*.py` | Reproducible generators (kiutils). Re-run to regenerate any output. |
| `BOM.csv` | Bill of materials with LCSC part numbers. |

## How to finish it (on your bench, in KiCad 7/8)
1. Open `pmw3610_daughterboard.kicad_pro`. The board opens with all 14 components
   placed and every net assigned (ratsnest visible). Custom footprints resolve via
   `fp-lib-table`; passives resolve from KiCad's stock libraries.
2. **Route** the tracks (follow the ratsnest / `SCHEMATIC.md`). Pour GND on both layers.
3. Add the **LM18-LSI lens** mechanical outline / mounting to match your ball-side
   case pocket, and confirm the board outline + lens optical center against the
   stock Keyball ball-side dimensions.
4. Run **DRC** (2-layer, JLCPCB/PCBway default rules — 0.15 mm track/space, 0.3 mm hole).
5. Export gerbers + drill → order at PCBway (2-layer, 1.6 mm, HASL, ≤100×100 mm, qty 5–10).

## Honest limitations (read before fabbing)
- **Not auto-routed.** This deliverable places and nets the board correctly; laying
  the copper and passing DRC is done in KiCad. Hand-authored tracks that can't be
  DRC-checked here would be less trustworthy than you routing a correct placement.
- **Outline + lens position are baseline** (24×32 mm from the proven siderakb board).
  Verify against the physical Keyball ball-side pocket before ordering — this is the
  one mechanical fit item that needs your measurement or the ball-side gerber.
- **Passive footprints** reference KiCad stock libraries; they render on open. The
  two custom parts are fully self-contained in `pmw3610_kb.pretty/`.

## ZMK
See `DESIGN.md` for the `&spi1` trackball node. MOTION → P0.31 (active-low, pull-up);
SCLK P1.11, SDIO P0.10 (3-wire), NCS P0.09. Driver: `pixart,pmw3610`
(inorichi/badjeff or in-tree Zephyr).
