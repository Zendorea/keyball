#!/usr/bin/env python3
"""
Emit the KiCad netlist (.net) + a human-readable SCHEMATIC.md from the single
source-of-truth component/net tables shared with make_board.py.

The .net is a standard KiCad (kicad_sexpr) netlist eeschema/pcbnew both consume;
importing it into a fresh schematic or updating the PCB from it reproduces the
full connectivity. SCHEMATIC.md is the drawing reference (block diagram + the
net-by-net connection list) to open alongside the board in KiCad.
"""
import os

HERE = os.path.dirname(__file__)

# (ref, value, footprint) — footprint as lib:entry KiCad resolves on open
COMPS = [
    ("U1", "PMW3610DM-SUDU", "pmw3610_kb:PMW3610DM-SUDU"),
    ("U2", "TLV74318PDBVR",  "Package_TO_SOT_SMD:SOT-23-5"),
    ("J1", "Conn_Keyball_8pin", "pmw3610_kb:Conn_Keyball_8pin"),
    ("C1", "3.3uF",  "Capacitor_SMD:C_0805_2012Metric"),
    ("C2", "100nF",  "Capacitor_SMD:C_0603_1608Metric"),
    ("C3", "100nF",  "Capacitor_SMD:C_0603_1608Metric"),
    ("C4", "100nF",  "Capacitor_SMD:C_0603_1608Metric"),
    ("C5", "10nF",   "Capacitor_SMD:C_0603_1608Metric"),
    ("C6", "10uF",   "Capacitor_SMD:C_0805_2012Metric"),
    ("C7", "10nF",   "Capacitor_SMD:C_0603_1608Metric"),
    ("C8", "1uF",    "Capacitor_SMD:C_0603_1608Metric"),
    ("C9", "1uF",    "Capacitor_SMD:C_0603_1608Metric"),
    ("R1", "10k",    "Resistor_SMD:R_0603_1608Metric"),
    ("R2", "10k DNP","Resistor_SMD:R_0603_1608Metric"),
]

# net -> list of (ref, pad)
NETLIST = {
    "+3V3":   [("J1","1"),("U2","1"),("U2","3"),("C3","1"),("C8","1"),
               ("R1","1"),("R2","1"),("U1","6")],
    "+1V8":   [("U2","5"),("C1","1"),("C2","1"),("C4","1"),("C9","1"),("U1","14")],
    "GND":    [("J1","2"),("J1","7"),("U2","2"),("C1","2"),("C2","2"),("C3","2"),
               ("C4","2"),("C6","2"),("C7","2"),("C8","2"),("C9","2"),("U1","11")],
    "SCLK":   [("J1","3"),("U1","3")],
    "SDIO":   [("J1","4"),("U1","2")],
    "NCS":    [("J1","5"),("U1","5")],
    "MOTION": [("J1","6"),("U1","8"),("R2","2")],
    "NRESET": [("U1","7"),("R1","2")],
    "CP":     [("U1","12"),("C5","1")],
    "CN":     [("U1","13"),("C5","2")],
    "VCP":    [("U1","9"),("C7","1")],
    "PASST":  [("U1","10"),("C6","1")],
}


def emit_net():
    lines = ['(export (version "E")', '  (components']
    for ref, val, fp in COMPS:
        lines.append(f'    (comp (ref "{ref}") (value "{val}") (footprint "{fp}"))')
    lines.append('  )')
    lines.append('  (nets')
    for i, (net, nodes) in enumerate(NETLIST.items(), start=1):
        lines.append(f'    (net (code "{i}") (name "{net}")')
        for ref, pad in nodes:
            lines.append(f'      (node (ref "{ref}") (pin "{pad}"))')
        lines.append('    )')
    lines.append('  )')
    lines.append(')')
    p = os.path.join(HERE, "pmw3610_daughterboard.net")
    open(p, "w").write("\n".join(lines) + "\n")
    print("wrote", p)


def emit_schematic_md():
    md = ["# PMW3610 Daughterboard — Schematic (connection reference)",
          "",
          "Net-by-net connection list. This is the source of truth the `.net` and",
          "`.kicad_pcb` are generated from. Open the board in KiCad, then route to",
          "match these nets. Block diagram:",
          "",
          "```",
          "  Keyball 8-pin (J1)          PMW3610 (U1, 16-DIP)",
          "  1 VCC  ---+---------------- 6 VDDIO",
          "           +--[U2 LDO 3V3->1V8]-- 14 VDD",
          "  2 GND ----+---------------- 11 GND",
          "  3 SCLK --------------------- 3 SCLK",
          "  4 SDIO --------------------- 2 SDIO (3-wire: MOSI=MISO)",
          "  5 NCS  --------------------- 5 NCS",
          "  6 MOT  --------------------- 8 MOTION  (+R2 opt pull-up to 3V3)",
          "  7 GND ----+",
          "  8 NC",
          "                   7 NRESET --[R1 10k]-- +3V3",
          "                   12/13 CP/CN --[C5 10n]",
          "                   9 VCP --[C7 10n]-- GND",
          "                   10 PASST --[C6 10u]-- GND",
          "```",
          "",
          "## Nets"]
    for net, nodes in NETLIST.items():
        ns = ", ".join(f"{r}.{p}" for r, p in nodes)
        md.append(f"- **{net}**: {ns}")
    md += ["",
           "## Notes",
           "- U2 TLV74318 SOT-23-5: 1=IN, 2=GND, 3=EN(tie +3V3), 4=NC, 5=OUT(+1V8).",
           "- R2 is DNP by default; populate only if not using the nice!nano internal",
           "  pull-up on the MOTION GPIO (P0.31).",
           "- U1 pins 1/15/16 = VCSEL (internal to lens optics), pin 4 = NC — no net.",
           "- Lens LM18-LSI seats over U1; optical center = board center."]
    p = os.path.join(HERE, "SCHEMATIC.md")
    open(p, "w").write("\n".join(md) + "\n")
    print("wrote", p)


if __name__ == "__main__":
    emit_net()
    emit_schematic_md()
