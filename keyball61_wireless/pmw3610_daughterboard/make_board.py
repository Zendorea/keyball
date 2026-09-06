#!/usr/bin/env python3
"""
Generate the PMW3610 Keyball61 daughterboard .kicad_pcb (kiutils, KiCad 6/7).

PLACED + FULLY NET-ASSIGNED board: custom footprints (sensor, 8-pin connector)
load from the local .pretty; passives reference KiCad STOCK footprint libraries
(Capacitor_SMD / Resistor_SMD / Package_TO_SOT_SMD) which resolve when opened in
KiCad. NOT auto-routed: finish tracks + pours + DRC in KiCad before gerbers.

Board 24 x 32 mm, 2-layer, 1.6 mm. Sensor centered (lens optical center = center).

Netlist (siderakb-derived, PMW3610 3-wire SPI @ 1.8V core, 3.3V IO):
  +3V3  : J1.VCC, U2.IN(1), U2.EN(3), C8+, sensor VDDIO(6), R1 top, C3+
  +1V8  : U2.OUT(5), C9+, sensor VDD(14), C1+, C2+, C4+
  GND   : J1.GND x2, U2.GND(2), all cap-, R return, sensor GND(11)
  SCLK/SDIO/NCS : J1<->sensor(3/2/5)
  MOTION: J1.6 <-> sensor(8), R2 top (opt pull-up)
  NRESET: sensor(7) <-> R1 bottom (pull-up to +3V3)
  CP/CN : sensor 12/13 <-> C5
  VCP   : sensor 9 <-> C7
  PASST : sensor 10 <-> C6
"""
import os
from kiutils.board import Board
from kiutils.footprint import (Footprint, Net as FpNet, Pad, DrillDefinition,
                               FpText, FpLine, Attributes)
from kiutils.items.common import Position, Net, Effects, Font
from kiutils.items.gritems import GrLine

HERE = os.path.dirname(__file__)
PRETTY = os.path.join(HERE, "pmw3610_kb.pretty")
W, H = 24.0, 32.0

NETS = ["", "GND", "+3V3", "+1V8", "SCLK", "SDIO", "NCS", "MOTION",
        "NRESET", "CP", "CN", "VCP", "PASST"]
NETID = {n: i for i, n in enumerate(NETS)}

# ---- SMD footprint synthesizers (so passives are self-contained + placeable) ----
def smd_pad(number, x, y, w, h, shape="roundrect"):
    p = Pad(number=str(number), type="smd", shape=shape,
            position=Position(x, y), size=Position(w, h),
            layers=["F.Cu", "F.Paste", "F.Mask"])
    if shape == "roundrect":
        p.roundrectRatio = 0.25
    return p


def _decorate(fp, nick, entry, value):
    fp.libraryNickname = nick
    fp.entryName = entry
    fp.generator = "kiutils"
    fp.layer = "F.Cu"
    fp.attributes = Attributes(type="smd")
    fp.graphicItems.append(FpText(type="reference", text="REF**",
                                  position=Position(0, -1.5), layer="F.SilkS",
                                  effects=Effects(font=Font())))
    fp.graphicItems.append(FpText(type="value", text=value,
                                  position=Position(0, 1.5), layer="F.Fab",
                                  effects=Effects(font=Font())))
    return fp


def fp_chip(nick, entry, value, body_l, pad_w, pad_h, gap):
    """2-pad chip resistor/cap. gap = inner edge-to-edge; pads centered +/-."""
    fp = Footprint()
    _decorate(fp, nick, entry, value)
    cx = gap / 2 + pad_w / 2
    fp.pads.append(smd_pad(1, -cx, 0, pad_w, pad_h))
    fp.pads.append(smd_pad(2, +cx, 0, pad_w, pad_h))
    return fp


def fp_sot235(nick, entry, value):
    """SOT-23-5: pins 1,2,3 bottom (pitch 0.95), 4,5 top."""
    fp = Footprint()
    _decorate(fp, nick, entry, value)
    p = 0.95
    ys = 1.1
    xs = [-p, 0, p]
    for i, x in enumerate(xs, start=1):
        fp.pads.append(smd_pad(i, x, ys, 0.6, 0.9))
    fp.pads.append(smd_pad(4, p, -ys, 0.6, 0.9))
    fp.pads.append(smd_pad(5, -p, -ys, 0.6, 0.9))
    return fp


def C0603(v): return fp_chip("Capacitor_SMD", "C_0603_1608Metric", v, 1.6, 0.9, 0.95, 0.8)
def C0805(v): return fp_chip("Capacitor_SMD", "C_0805_2012Metric", v, 2.0, 1.15, 1.4, 1.0)
def R0603(v): return fp_chip("Resistor_SMD", "R_0603_1608Metric", v, 1.6, 0.9, 0.95, 0.8)


def load_custom(name):
    return Footprint.from_file(os.path.join(PRETTY, name + ".kicad_mod"))


# ---- component instances: ref -> (factory, x, y, rot, value) ----
# custom two are loaded from .pretty; rest synthesized as stock-equivalent SMD.
COMPONENTS = [
    ("U1", "custom:PMW3610DM-SUDU", 12.0, 12.0, 0, "PMW3610DM-SUDU"),
    ("J1", "custom:Conn_Keyball_8pin", 12.0, 30.0, 0, "Conn_Keyball_8pin"),
    ("U2", "sot235", 4.0, 24.0, 0, "TLV74318PDBVR"),
    ("C1", "C0805", 8.0, 22.0, 0, "3.3uF"),
    ("C2", "C0603", 8.0, 24.0, 0, "100nF"),
    ("C3", "C0603", 8.0, 26.0, 0, "100nF"),
    ("C4", "C0603", 16.0, 22.0, 0, "100nF"),
    ("C5", "C0603", 18.0, 12.0, 90, "10nF"),
    ("C6", "C0805", 18.0, 16.0, 0, "10uF"),
    ("C7", "C0603", 6.0, 12.0, 90, "10nF"),
    ("C8", "C0603", 2.0, 22.0, 90, "1uF"),
    ("C9", "C0603", 2.0, 26.0, 90, "1uF"),
    ("R1", "R0603", 20.0, 10.0, 90, "10k"),
    ("R2", "R0603", 20.0, 14.0, 90, "10k"),  # optional MOTION pull-up (DNP)
]

# pad -> net for every ref
PADNETS = {
    "U1": {2: "SDIO", 3: "SCLK", 5: "NCS", 6: "+3V3", 7: "NRESET", 8: "MOTION",
           9: "VCP", 10: "PASST", 11: "GND", 12: "CP", 13: "CN", 14: "+1V8"},
    "J1": {1: "+3V3", 2: "GND", 3: "SCLK", 4: "SDIO", 5: "NCS", 6: "MOTION",
           7: "GND", 8: ""},
    # TLV74318 SOT-23-5: 1=IN, 2=GND, 3=EN, 4=NC, 5=OUT
    "U2": {1: "+3V3", 2: "GND", 3: "+3V3", 5: "+1V8"},
    "C1": {1: "+1V8", 2: "GND"},
    "C2": {1: "+1V8", 2: "GND"},
    "C3": {1: "+3V3", 2: "GND"},
    "C4": {1: "+1V8", 2: "GND"},
    "C5": {1: "CP", 2: "CN"},
    "C6": {1: "PASST", 2: "GND"},
    "C7": {1: "VCP", 2: "GND"},
    "C8": {1: "+3V3", 2: "GND"},
    "C9": {1: "+1V8", 2: "GND"},
    "R1": {1: "+3V3", 2: "NRESET"},
    "R2": {1: "+3V3", 2: "MOTION"},
}

FACTORY = {"C0603": C0603, "C0805": C0805, "R0603": R0603, "sot235":
           lambda v: fp_sot235("Package_TO_SOT_SMD", "SOT-23-5", v)}


def build_fp(kind, value):
    if kind.startswith("custom:"):
        return load_custom(kind.split(":", 1)[1])
    return FACTORY[kind](value)


def main():
    b = Board.create_new()
    b.nets = [Net(NETID[n], n) for n in NETS]

    pts = [(0, 0), (W, 0), (W, H), (0, H), (0, 0)]
    for i in range(len(pts) - 1):
        b.graphicItems.append(GrLine(start=Position(*pts[i]),
                               end=Position(*pts[i + 1]),
                               layer="Edge.Cuts", width=0.1))

    for ref, kind, x, y, rot, value in COMPONENTS:
        fp = build_fp(kind, value)
        fp.position = Position(x, y, rot)
        for gi in fp.graphicItems:
            if getattr(gi, "type", None) == "reference":
                gi.text = ref
            if getattr(gi, "type", None) == "value":
                gi.text = value
        pn = PADNETS.get(ref, {})
        for pad in fp.pads:
            try:
                num = int(pad.number)
            except ValueError:
                continue
            net = pn.get(num, "")
            if net:
                pad.net = FpNet(NETID[net], net)
        b.footprints.append(fp)

    out = os.path.join(HERE, "pmw3610_daughterboard.kicad_pcb")
    b.to_file(out)
    Board.from_file(out)
    print("wrote+validated", out)
    print("components:", len(b.footprints))
    # sanity: report unconnected pads count
    total = sum(len(f.pads) for f in b.footprints)
    netted = sum(1 for f in b.footprints for p in f.pads if p.net and p.net.name)
    print(f"pads {total}, netted {netted}")


if __name__ == "__main__":
    main()
