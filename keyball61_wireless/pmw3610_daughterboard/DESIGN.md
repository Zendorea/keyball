# PMW3610 Trackball Daughterboard — Keyball61 Wireless (nice!nano / ZMK)

Purpose-built replacement for the stock Keyball61 PMW3360 ball-reader board.
Swaps the power-hungry PMW3360 (kills battery on wireless) for the low-power
**PMW3610**, and adds a **MOTION** interrupt line so ZMK runs the sensor
interrupt-driven (best battery life) instead of polled.

Fork of Yowkees/keyball → github.com/Zendorea/keyball, branch `feat/pmw3610-wireless`.

## Sensor: PMW3610DM-SUDU
- 16-pin optical DIP, 3-wire SPI (single bidirectional SDIO), 1.8 V core.
- Requires on-board LDO (3.3 V → 1.8 V) + charge-pump/decoupling network.
- Lens: **LM18-LSI** (PixArt), matched to the PMW3610. NOT the 3360's LM19-LSI.

## Electrical baseline (proven — siderakb/pmw3610-pcb, CERN-OHL-P)
| Ref | Value | Purpose |
|-----|-------|---------|
| U1  | PMW3610DM-SUDU | sensor |
| U2  | TLV74318PDBVR (SOT-23-5, 1.8 V LDO) | derive VDD from 3.3 V |
| C1  | 3.3 µF/16 V 0805 | VDD bulk |
| C2  | 100 nF 0603 | VDD decouple |
| C3  | 100 nF 0603 | VDDIO decouple |
| C4  | 100 nF 0603 | sensor bulk (near pins) |
| C5  | 10 nF 0603 | charge pump CP–CN |
| C6  | 10 µF 0805 | PASS_T |
| C7  | 10 nF 0603 | VCP |
| C8  | 1 µF 0603 | LDO IN |
| C9  | 1 µF 0603 | LDO OUT |
| R1  | 10 kΩ 0603 | NRESET pull-up → VDDIO |
| R2  | 10 kΩ 0603 (optional, DNP) | MOTION pull-up → VDDIO (belt-and-suspenders; ZMK also enables internal pull-up) |

VDDIO = 3.3 V (nice!nano logic). Sensor VDD = 1.8 V from U2.

## Host connector — 8-pin, 2.54 mm pitch (matches Keyball Mac8 L-header geometry)
Stock Keyball connector = 7 pads @ 2.54 mm pitch, 1.5×1.5 mm, single row (Mac8_L_7pin_contact_NEW2023).
We extend to **8 pins** to carry MOTION as a real trace (no flying wire).

| Pin | Net   | ZMK pin (right half) |
|-----|-------|----------------------|
| 1   | VCC (3.3 V) | RAW/VCC |
| 2   | GND   | GND |
| 3   | SCLK  | P1.11 (&spi1 SCK) |
| 4   | SDIO  | P0.10 (&spi1 MOSI=MISO) |
| 5   | NCS   | P0.09 (&spi1 cs, active-low) |
| 6   | MOTION| P0.31 (GPIO IRQ, active-low + pull-up) |
| 7   | GND   | GND (signal-return / shield) |
| 8   | (key/NC or NRESET) | leave NC; NRESET has internal + R1 pull-up |

Pitch 2.54 mm, pads 1.5×1.5 mm to match the stock mating header. Pin-1 marked on silk.

## Mechanical
- Baseline outline: 23.5 × 31.5 mm (siderakb proven), 2-layer, 1.6 mm, HASL.
- LM18-LSI lens: optical center on board center; 4× M2 alignment/mount as needed.
- Lens working distance (LM18-LSI): 2.2 / 2.4 / 2.6 mm (min/typ/max) lens ref plane → ball surface.
- Verify final outline + lens-center against the Keyball ball-side case pocket before fab.

## ZMK config (right half, PMW3610 on &spi1)
```
&spi1 {
    compatible = "nordic,nrf-spim";
    status = "okay";
    pinctrl-0 = <&spi1_default>;   /* SCK P1.11, MOSI P0.10 */
    cs-gpios = <&gpio0 9 GPIO_ACTIVE_LOW>;   /* NCS P0.09 */
    trackball: trackball@0 {
        compatible = "pixart,pmw3610";
        reg = <0>;
        spi-max-frequency = <2000000>;
        irq-gpios = <&gpio0 31 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>;  /* MOTION P0.31 */
    };
};
```

## Status
- [ ] Stage 1: daughterboard schematic
- [ ] Stage 1: daughterboard PCB + footprints (PMW3610, 8-pin edge connector, LM18-LSI)
- [ ] Stage 1: DRC + gerbers
- [ ] Bench review in KiCad before PCBway order

## Manufacturing notes (PCBway)
- 2-layer, 1.6 mm, HASL, ≤100×100 mm → $5 promo tier; qty 5–10.
- Fine-pitch sensor is hand-solderable (2.54 mm DIP pads); PCBA optional.
