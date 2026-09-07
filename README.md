# Keyball61 Wireless (PMW3610 / nice!nano / ZMK)

A fork of [Yowkees/keyball](https://github.com/Yowkees/keyball) for converting a
**Keyball61** (holykeebs Keyball61 rev2) to a **fully wireless** build:
**nice!nano v2 + ZMK**, with the power-hungry PMW3360 trackball sensor replaced by
the low-power **PMW3610**.

This fork holds the **hardware** side of that conversion — the custom PMW3610
sensor daughterboard. The **firmware** (ZMK) lives in a separate repo.

## What's here

- **[`keyball61_wireless/pmw3610_daughterboard/`](keyball61_wireless/pmw3610_daughterboard/)**
  — the PMW3610 trackball daughterboard: KiCad source, reproducible build
  pipeline, DRC-clean gerbers (ordered from PCBway), BOM, and full design notes.
  A drop-in replacement for the stock Keyball61 ball-reader board that keeps the
  original 7-pin connector and adds a MOTION interrupt line. **See its README.**
- **`keyball61/`** — the upstream Yowkees Keyball61 hardware design data (kept for
  reference: case, PCB, dimensions the daughterboard indexes to).

## Firmware (separate repo)

The wireless ZMK config is **`zmk-config-keyball61-wireless`** (standalone, as ZMK
configs must be). Trackball on `&spi1`: SCK P1.13, SDIO P0.10 (3-wire), CS P0.09,
MOTION P1.11, 2 MHz — based on the proven `tangbonze/zmk-config-Keyball61`.

## Project status

- ✅ Daughterboard: designed, DRC-clean, gerbers ordered (PCBway, ENIG, 1.0 mm)
- ✅ Parts sourced: PMW3610+LM18-LSI (AliExpress), passives/LDO (LCSC), 34 mm ball
- ✅ ZMK config: built (separate repo)
- ⬜ Assemble + flash when hardware arrives
- ⬜ (optional) main-board fork: nice!nano + nice!view

## Credits

Base keyboard design © [Yowkees / Keyball](https://github.com/Yowkees/keyball)
(see `LICENSE`). PMW3610 reference designs: siderakb / badjeff. Kit: holykeebs.
