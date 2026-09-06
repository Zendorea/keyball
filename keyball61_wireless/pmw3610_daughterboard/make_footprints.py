#!/usr/bin/env python3
"""
Generate the KiCad footprint library for the PMW3610 Keyball61 daughterboard.

Custom footprints (kiutils, KiCad 6/7 .kicad_mod):
  PMW3610DM-SUDU     : 16-pin DIP optical sensor, 2.54 mm pitch, rows 10.16 mm apart.
  Conn_Keyball_8pin  : single-row 8-pad, 2.54 mm pitch, 1.5 mm round pads,
                       matching stock Keyball Mac8_L_7pin geometry + 1 pad (MOTION).

Run:  make_footprints.py  ->  ./pmw3610_kb.pretty/*.kicad_mod
"""
import os
from kiutils.footprint import (Footprint, Pad, DrillDefinition,
                               FpText, FpLine, Attributes)
from kiutils.items.common import Position, Effects, Font

OUT = os.path.join(os.path.dirname(__file__), "pmw3610_kb.pretty")
os.makedirs(OUT, exist_ok=True)


def th_pad(number, x, y, drill=0.8, size=1.5, shape="circle"):
    return Pad(
        number=str(number), type="thru_hole", shape=shape,
        position=Position(x, y), size=Position(size, size),
        drill=DrillDefinition(diameter=drill),
        layers=["*.Cu", "*.Mask"],
    )


def line(fp, x0, y0, x1, y1, layer="F.SilkS", width=0.12):
    fp.graphicItems.append(FpLine(start=Position(x0, y0), end=Position(x1, y1),
                                  layer=layer, width=width))


def rect(fp, w, h, cx=0.0, cy=0.0, layer="F.SilkS", width=0.12):
    x0, y0, x1, y1 = cx - w/2, cy - h/2, cx + w/2, cy + h/2
    line(fp, x0, y0, x1, y0, layer, width)
    line(fp, x1, y0, x1, y1, layer, width)
    line(fp, x1, y1, x0, y1, layer, width)
    line(fp, x0, y1, x0, y0, layer, width)


def txt(fp, ttype, text, x, y, layer):
    fp.graphicItems.append(FpText(type=ttype, text=text, position=Position(x, y),
                                  layer=layer, effects=Effects(font=Font())))


def new_fp(entry):
    fp = Footprint()
    fp.libraryNickname = "pmw3610_kb"
    fp.entryName = entry
    fp.generator = "kiutils"
    fp.layer = "F.Cu"
    fp.attributes = Attributes(type="through_hole")
    txt(fp, "reference", "REF**", 0, -9, "F.SilkS")
    txt(fp, "value", entry, 0, 9, "F.Fab")
    return fp


# ---- PMW3610 16-DIP ----
def make_pmw3610():
    fp = new_fp("PMW3610DM-SUDU")
    pitch = 2.54
    row_dx = 10.16 / 2.0
    y0 = -(7 * pitch) / 2.0
    for i in range(8):
        n = i + 1
        fp.pads.append(th_pad(n, -row_dx, y0 + i * pitch,
                              shape="rect" if n == 1 else "circle"))
    for i in range(8):
        n = 16 - i
        fp.pads.append(th_pad(n, +row_dx, y0 + i * pitch))
    rect(fp, 12.0, 10.9 + 2 * pitch, layer="F.Fab")
    rect(fp, 12.6, 10.9 + 2 * pitch + 0.5, layer="F.SilkS")
    txt(fp, "user", "1", -row_dx, y0 - 1.8, "F.SilkS")
    txt(fp, "user", "LM18-LSI lens over sensor", 0, 12, "F.Fab")
    return fp


# ---- 8-pin Keyball-mate connector ----
# net order: 1 VCC, 2 GND, 3 SCLK, 4 SDIO, 5 NCS, 6 MOTION, 7 GND, 8 NC/key
def make_conn8():
    fp = new_fp("Conn_Keyball_8pin")
    pitch = 2.54
    x0 = -(7 * pitch) / 2.0
    nets = ["VCC", "GND", "SCLK", "SDIO", "NCS", "MOT", "GND", "NC"]
    for i in range(8):
        n = i + 1
        fp.pads.append(th_pad(n, x0 + i * pitch, 0.0, drill=0.9, size=1.5,
                              shape="rect" if n == 1 else "circle"))
        txt(fp, "user", nets[i], x0 + i * pitch, -2.4, "F.SilkS")
    rect(fp, 8 * pitch + 1.0, 3.2, layer="F.SilkS")
    return fp


def save(fp, name):
    path = os.path.join(OUT, name + ".kicad_mod")
    fp.to_file(path)
    Footprint.from_file(path)  # validate re-parse
    print("wrote+validated", path)


if __name__ == "__main__":
    save(make_pmw3610(), "PMW3610DM-SUDU")
    save(make_conn8(), "Conn_Keyball_8pin")
    print("done")
