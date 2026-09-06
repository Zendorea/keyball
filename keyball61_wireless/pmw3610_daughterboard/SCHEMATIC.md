# PMW3610 Daughterboard — Schematic (connection reference)

Net-by-net connection list. This is the source of truth the `.net` and
`.kicad_pcb` are generated from. Open the board in KiCad, then route to
match these nets. Block diagram:

```
  Keyball 8-pin (J1)          PMW3610 (U1, 16-DIP)
  1 VCC  ---+---------------- 6 VDDIO
           +--[U2 LDO 3V3->1V8]-- 14 VDD
  2 GND ----+---------------- 11 GND
  3 SCLK --------------------- 3 SCLK
  4 SDIO --------------------- 2 SDIO (3-wire: MOSI=MISO)
  5 NCS  --------------------- 5 NCS
  6 MOT  --------------------- 8 MOTION  (+R2 opt pull-up to 3V3)
  7 GND ----+
  8 NC
                   7 NRESET --[R1 10k]-- +3V3
                   12/13 CP/CN --[C5 10n]
                   9 VCP --[C7 10n]-- GND
                   10 PASST --[C6 10u]-- GND
```

## Nets
- **+3V3**: J1.1, U2.1, U2.3, C3.1, C8.1, R1.1, R2.1, U1.6
- **+1V8**: U2.5, C1.1, C2.1, C4.1, C9.1, U1.14
- **GND**: J1.2, J1.7, U2.2, C1.2, C2.2, C3.2, C4.2, C6.2, C7.2, C8.2, C9.2, U1.11
- **SCLK**: J1.3, U1.3
- **SDIO**: J1.4, U1.2
- **NCS**: J1.5, U1.5
- **MOTION**: J1.6, U1.8, R2.2
- **NRESET**: U1.7, R1.2
- **CP**: U1.12, C5.1
- **CN**: U1.13, C5.2
- **VCP**: U1.9, C7.1
- **PASST**: U1.10, C6.1

## Notes
- U2 TLV74318 SOT-23-5: 1=IN, 2=GND, 3=EN(tie +3V3), 4=NC, 5=OUT(+1V8).
- R2 is DNP by default; populate only if not using the nice!nano internal
  pull-up on the MOTION GPIO (P0.31).
- U1 pins 1/15/16 = VCSEL (internal to lens optics), pin 4 = NC — no net.
- Lens LM18-LSI seats over U1; optical center = board center.
