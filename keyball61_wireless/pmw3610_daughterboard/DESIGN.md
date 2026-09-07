# PMW3610 Trackball Daughterboard — Keyball61 Wireless (nice!nano / ZMK)

Purpose-built PMW3610 replacement for the stock Keyball61 PMW3360 ball-reader
board, for a nice!nano/ZMK wireless build (low power). Datasheet-faithful optical
mounting. DRC-clean.

## Final specs
- Outline: 23.0 x 25.0 mm (original 22x25 + 1mm on the right so the MOTION hole
  sits on the connector's 2.54mm pitch at full pad size). 1.0mm thick, 2-layer.
- Optics: lens slot open to the top edge, sized to the LM18-LSI lens body
  (8.25 x 12.9mm), between the sensor pin columns. Guide-post hole (GP1, Ø0.9mm).
  PMW3610 sensor optical center at original ball-facing position.
- Connector: stock Keyball 7-pin (SCLK,SDIO,GND,VCC,GND,NCS,NRESET) at the EXACT
  original 2.54mm-pitch positions -> drops into a stock Keyball main board.
- MOTION: separate solder hole (MOT) on the same 2.54mm pitch as the connector,
  same 1.5mm pad / 0.9mm drill. Wire it to a spare nice!nano GPIO (P0.31) on the
  stock board, or route it as a trace on a forked main board.
- Full PMW3610 support circuit: TLV74318 1.8V LDO (U2) + charge-pump/decoupling
  caps + NRESET pull-up. All parts ABOVE the connector line (nothing fouls the
  90-degree main-board joint). GND ground plane on B.Cu.
- Placement per IPC-7351/Eurocircuits: 0603 >=2.8mm pitch, 0805 >=3.2mm.

## Datasheet Z-stack (PixArt, saved in ../../../pmw3610_datasheets/)
- Ball surface -> lens reference plane = 2.4mm typ (2.2/2.6 min/max), +/-0.2mm DOF.
- Ball surface -> sensor pin reference plane (PCB top copper) = 8.35mm typ.
- PCB thickness does NOT set focus (lens indexes to the pin plane); 1.0mm chosen
  for lens/ball clearance. Verify base-plate/housing standoff at assembly.

## Reproducible build pipeline (KiCad 10 pcbnew + Freerouting 2.4.1)
  make_footprints_v2.py  -> custom footprints (sensor, 7-pin conn, MOTION pad, lens)
  build_board_22x25.py   -> place + net + design rules (pcbnew)
  export_dsn.py          -> Specctra DSN
  Freerouting (headless, -mt 1, --router.via_costs=30, -inc GND for pour route)
  import_ses.py          -> import routed session
  pour_gnd.py            -> B.Cu GND pour (solid pad connection)
  finish_22x25.py        -> GND stitching vias + guide-post hole
  kicad-cli pcb drc / export gerbers,drill

## DRC status
0 unrouted, 0 unconnected, 0 electrical violations. 4 courtyard_overlap
advisories remain (IPC keep-out for rework room, NOT fab-blocking; JLCPCB/PCBway
build fine). See board_final.png.

## Fab (PCBway)
2-layer, 1.0mm, HASL, qty 5-10. Upload pmw3610_daughterboard_gerbers.zip.

## Verify before ordering
1. Sensor/lens standoff vs your trackball housing (base-plate sets focus).
2. GP1 guide-post position vs your actual LM18-LSI lens posts.
