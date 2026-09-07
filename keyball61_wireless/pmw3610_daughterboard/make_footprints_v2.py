#!/usr/bin/env python3
"""
Footprint library for the PMW3610 Keyball daughterboard (real 22x25mm geometry).

Conn_Keyball_8pin_v2 : matches the ORIGINAL Keyball ball_sensor 7-pin connector
  EXACTLY (7 round 1.5mm pads at 2.54mm pitch, centered), then adds an 8th pad
  (MOTION) to the LEFT of pin 1 keeping the original 7 in place -> still mates a
  stock Keyball main board on pins 1-7.

  Original pad X (board-centered, X=11.0 is board center, board is 22mm wide):
    p1..p7 at X = 3.38,5.92,8.46,11.00,13.54,16.08,18.62  (from left edge)
  In footprint-local coords centered on the connector midpoint (X=11.0):
    p1..p7 at -7.62,-5.08,-2.54,0,+2.54,+5.08,+7.62
  MOTION p8 added at -10.16 (left of p1).

PMW3610_SMD : the PMW3610DM-SUDU as a molded DIP mounted ball-facing, with the
  LM18-LSI lens envelope marked. Uses the community 2.54mm/1.78mm DIP pad pattern.
  (Lens sits on TOP of the IC facing the ball; NO board cutaway.)
"""
import os
from kiutils.footprint import (Footprint, Pad, DrillDefinition, FpText, FpLine,
                               Attributes)
from kiutils.items.common import Position, Effects, Font

OUT = os.path.join(os.path.dirname(__file__), "pmw3610_kb.pretty")
os.makedirs(OUT, exist_ok=True)


def th_pad(number, x, y, drill, size, shape="circle"):
    return Pad(number=str(number), type="thru_hole", shape=shape,
               position=Position(x, y), size=Position(size, size),
               drill=DrillDefinition(diameter=drill), layers=["*.Cu", "*.Mask"])


def line(fp, x0, y0, x1, y1, layer="F.SilkS", w=0.12):
    fp.graphicItems.append(FpLine(start=Position(x0, y0), end=Position(x1, y1),
                                  layer=layer, width=w))


def rect(fp, w, h, cx, cy, layer="F.SilkS", width=0.12):
    x0, y0, x1, y1 = cx-w/2, cy-h/2, cx+w/2, cy+h/2
    line(fp, x0, y0, x1, y0, layer, width); line(fp, x1, y0, x1, y1, layer, width)
    line(fp, x1, y1, x0, y1, layer, width); line(fp, x0, y1, x0, y0, layer, width)


def txt(fp, t, s, x, y, layer):
    fp.graphicItems.append(FpText(type=t, text=s, position=Position(x, y),
                                  layer=layer, effects=Effects(font=Font())))


def new_fp(entry, kind="through_hole"):
    fp = Footprint(); fp.libraryNickname = "pmw3610_kb"; fp.entryName = entry
    fp.generator = "kiutils"; fp.layer = "F.Cu"
    fp.attributes = Attributes(type=kind)
    txt(fp, "reference", "REF**", 0, -3, "F.SilkS")
    txt(fp, "value", entry, 0, 3, "F.Fab")
    return fp


def make_conn7_stock():
    """EXACT stock Keyball 7-pin connector: 7 pads @2.54mm, centered. No MOTION
    pin (that's a separate solder hole). Drops into a stock Keyball main board."""
    fp = new_fp("Conn_Keyball_7pin_stock")
    xs = {"1": -7.62, "2": -5.08, "3": -2.54, "4": 0.0, "5": 2.54, "6": 5.08, "7": 7.62}
    # stock Keyball J2 net order: P1/P2/P6/P7 data, P3/P5 GND, P4 VCC.
    nets = {"1":"SCLK","2":"SDIO","3":"GND","4":"VCC","5":"GND","6":"NCS","7":"NRESET"}
    for num in ["1","2","3","4","5","6","7"]:
        fp.pads.append(th_pad(num, xs[num], 0.0, drill=0.9, size=1.5,
                              shape="rect" if num=="1" else "circle"))
        txt(fp, "user", nets[num], xs[num], -1.8, "F.SilkS")
    rect(fp, 7*2.54 + 2.0, 3.0, 0, 0, layer="F.SilkS")
    txt(fp, "user", "stock Keyball 7-pin (MOTION = separate pad)", 0, 2.6, "F.Fab")
    return fp


def make_motion_pad():
    """Single labeled through-hole solder pad for the MOTION wire to a nice!nano
    GPIO. Used on both the stock-board build (flying wire) and the forked main
    board (routed trace to the pad)."""
    fp = new_fp("MOTION_solder_pad")
    fp.pads.append(th_pad("1", 0.0, 0.0, drill=0.9, size=1.5, shape="circle"))
    txt(fp, "user", "MOT", 0, -1.6, "F.SilkS")
    txt(fp, "user", "MOTION -> nice!nano GPIO (P0.31)", 0, 1.8, "F.Fab")
    return fp


def make_conn8_v2():
    fp = new_fp("Conn_Keyball_8pin_v2")
    pitch = 2.54
    # original 7 at -7.62..+7.62, MOTION added at -10.16
    xs = {"8": -9.2, "1": -7.62, "2": -5.08, "3": -2.54, "4": 0.0,
          "5": 2.54, "6": 5.08, "7": 7.62}
    # Real Keyball J2 order (from main-board netlist): P3/P5=GND, P4=VCC,
    # P1/P2/P6/P7 = the 4 data lines. PMW3610 is 3-wire, so we assign:
    #   P1=SCLK  P2=SDIO  P6=NCS  P7=NRESET   (P4=VCC, P3/P5=GND)  P8=MOTION(new)
    nets = {"1":"SCLK","2":"SDIO","3":"GND","4":"VCC","5":"GND",
            "6":"NCS","7":"NRESET","8":"MOT"}
    for num in ["1","2","3","4","5","6","7","8"]:
        fp.pads.append(th_pad(num, xs[num], 0.0, drill=0.9, size=1.5,
                              shape="rect" if num == "1" else "circle"))
        txt(fp, "user", nets[num], xs[num], -1.8, "F.SilkS")
    rect(fp, 8*pitch + 2.5, 3.0, 0, 0, layer="F.SilkS")
    txt(fp, "user", "P1-7 match stock Keyball J2; P8=MOTION (added)", 0, 2.6, "F.Fab")
    return fp


def make_pmw3610_smd():
    # 16-pin DIP, 2 rows 1.78mm pitch (community footprint), rows ~10.7mm apart.
    # Mounted ball-facing; LM18-LSI lens envelope 8.26 x 13.10 mm marked on F.Fab.
    fp = new_fp("PMW3610DM-SUDU-SMD", kind="through_hole")
    pitch = 1.78
    row_dx = 10.7/2.0
    y0 = -(7*pitch)/2.0
    for i in range(8):
        n = i+1
        fp.pads.append(th_pad(n, -row_dx, y0+i*pitch, drill=0.7, size=1.2,
                              shape="rect" if n == 1 else "circle"))
    for i in range(8):
        n = 16-i
        fp.pads.append(th_pad(n, +row_dx, y0+i*pitch, drill=0.7, size=1.2))
    # sensor body + lens envelope
    rect(fp, 12.0, 10.9+2*pitch, 0, 0, layer="F.Fab")
    rect(fp, 8.26, 13.10, 1.5, 0, layer="F.Fab")   # LM18-LSI lens envelope
    txt(fp, "user", "LM18-LSI lens (ball-facing, on TOP of IC)", 0, 12, "F.Fab")
    txt(fp, "user", "optical center", 1.5, 0, "F.Fab")
    txt(fp, "user", "1", -row_dx, y0-1.6, "F.SilkS")
    return fp


def save(fp, name):
    p = os.path.join(OUT, name + ".kicad_mod")
    fp.to_file(p); Footprint.from_file(p)
    print("wrote+validated", p)


if __name__ == "__main__":
    save(make_conn8_v2(), "Conn_Keyball_8pin_v2")
    save(make_conn7_stock(), "Conn_Keyball_7pin_stock")
    save(make_motion_pad(), "MOTION_solder_pad")
    save(make_pmw3610_smd(), "PMW3610DM-SUDU-SMD")
    print("done")
