#!/usr/bin/env python3
"""
Build the PMW3610 Keyball daughterboard v2 to the REAL geometry, with pcbnew.

- Outline: 22.0 x 25.0 mm (matches original Keyball ball_sensor), 1.6mm.
- OPTICS CUTAWAY: top-center slot 8.6 wide x 15.7 deep (X[6.7,15.3] from left,
  open at the TOP edge) -- because this PMW3610 module's optic is on the
  UNDERSIDE of the IC and the PCB would otherwise block it. Matches the original
  Keyball slot exactly so the optics hit the 34mm ball at the correct angle.
- Sensor optical center positioned OVER the slot.
- 8-pin connector: original 7 positions (2.54mm pitch, centered, 5.2mm from
  bottom) + MOTION as P8. Nets match stock Keyball J2.
- Passives placed clear of slot+sensor, in the lower/side bands.

Origin: board bottom-left = (0,0), Y up. Slot opens at TOP edge (y=25).

Run: /usr/bin/python3 build_board_v2.py
"""
import os, pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
PRETTY = os.path.join(HERE, "pmw3610_kb.pretty")
STOCK = "/usr/share/kicad/footprints"
OUT = os.path.join(HERE, "pmw3610_daughterboard.kicad_pcb")
W, H = 22.0, 25.0

def mm(v): return pcbnew.FromMM(v)

NETS = ["GND", "VCC", "+1V8", "SCLK", "SDIO", "NCS", "MOTION",
        "NRESET", "CP", "CN", "VCP", "PASST"]

# Board center X = 11.0. Connector row at Y=5.2 from bottom (original = 5.2).
# Slot: X[6.7,15.3], from top edge (Y=25) down to Y=9.3 (15.7 deep).
# Sensor: optical center over the slot, low enough that its pads sit below the
# slot bottom (Y<9.3) but the optic aperture is under the slot. Place U1 center
# so lens envelope (~13mm tall) spans the slot; sensor body centered at X=11.
COMPONENTS = [
    ("U1", "custom", "PMW3610DM-SUDU-SMD",     11.0, 12.5, 0,   "PMW3610DM-SUDU"),
    ("J1", "custom", "Conn_Keyball_8pin_v2",   11.0, 5.2,  0,   "Conn_Keyball_8pin"),
    # power section: bottom band below connector (Y<4), spaced
    ("U2", "Package_TO_SOT_SMD", "SOT-23-5",    3.5, 2.2, 0,    "TLV74318PDBVR"),
    ("C8", "Capacitor_SMD", "C_0603_1608Metric", 7.0, 2.2, 0,   "1uF"),
    ("C9", "Capacitor_SMD", "C_0603_1608Metric", 9.5, 2.2, 0,   "1uF"),
    ("C1", "Capacitor_SMD", "C_0805_2012Metric", 12.5, 2.2, 0,  "3.3uF"),
    ("C2", "Capacitor_SMD", "C_0603_1608Metric", 15.5, 2.2, 0,  "100nF"),
    ("C3", "Capacitor_SMD", "C_0603_1608Metric", 18.0, 2.2, 0,  "100nF"),
    # analog caps: sides, flanking the slot, clear of it (X<6.7 or X>15.3)
    ("C7", "Capacitor_SMD", "C_0603_1608Metric", 2.5, 12.0, 90, "10nF"),   # VCP left
    ("C4", "Capacitor_SMD", "C_0603_1608Metric", 2.5, 15.0, 90, "100nF"),  # VDD left
    ("C5", "Capacitor_SMD", "C_0603_1608Metric", 19.5, 12.0, 90, "10nF"),  # CP-CN right
    ("C6", "Capacitor_SMD", "C_0805_2012Metric", 19.5, 15.5, 90, "10uF"),  # PASST right
    ("R1", "Resistor_SMD", "R_0603_1608Metric",  19.5, 19.0, 90, "10k"),   # NRESET pull
    ("R2", "Resistor_SMD", "R_0603_1608Metric",   2.5, 19.0, 90, "10k"),   # MOTION pull (DNP)
]

# PMW3610 pin functions (community/datasheet): 2 SDIO,3 SCLK,5 NCS,6 VDDIO(VCC),
# 7 NRESET,8 MOTION,9 VCP,10 PASST,11 GND,12 CP,13 CN,14 VDD(+1V8).
PADNETS = {
    "U1": {"2":"SDIO","3":"SCLK","5":"NCS","6":"VCC","7":"NRESET","8":"MOTION",
           "9":"VCP","10":"PASST","11":"GND","12":"CP","13":"CN","14":"+1V8"},
    # connector v2: P1 SCLK,P2 SDIO,P3 GND,P4 VCC,P5 GND,P6 NCS,P7 NRESET,P8 MOTION
    "J1": {"1":"SCLK","2":"SDIO","3":"GND","4":"VCC","5":"GND","6":"NCS",
           "7":"NRESET","8":"MOTION"},
    "U2": {"1":"VCC","2":"GND","3":"VCC","5":"+1V8"},
    "C1": {"1":"+1V8","2":"GND"}, "C2": {"1":"+1V8","2":"GND"},
    "C3": {"1":"VCC","2":"GND"},  "C4": {"1":"+1V8","2":"GND"},
    "C5": {"1":"CP","2":"CN"},    "C6": {"1":"PASST","2":"GND"},
    "C7": {"1":"VCP","2":"GND"},  "C8": {"1":"VCC","2":"GND"},
    "C9": {"1":"+1V8","2":"GND"}, "R1": {"1":"VCC","2":"NRESET"},
    "R2": {"1":"VCC","2":"MOTION"},
}


def main():
    board = pcbnew.BOARD()
    for name in NETS:
        if board.FindNet(name) is None:
            board.Add(pcbnew.NETINFO_ITEM(board, name))
    ds = board.GetDesignSettings()
    ds.m_TrackMinWidth = mm(0.2); ds.m_MinClearance = mm(0.2)
    ds.m_MinThroughDrill = mm(0.3); ds.m_ViasMinSize = mm(0.6)
    try:
        d = board.GetAllNetClasses().get("Default")
        if d:
            d.SetTrackWidth(mm(0.25)); d.SetViaDiameter(mm(0.6))
            d.SetViaDrill(mm(0.3)); d.SetClearance(mm(0.2))
    except Exception as e:
        print("nc note:", e)

    def code(n): return board.FindNet(n).GetNetCode()

    def edge(x0, y0, x1, y1):
        s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(pcbnew.VECTOR2I(mm(x0), mm(y0)))
        s.SetEnd(pcbnew.VECTOR2I(mm(x1), mm(y1)))
        s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(mm(0.1)); board.Add(s)

    # Outline with top-center slot. Top edge is split by the slot opening.
    # bottom, right, top-right, slot-right-down, slot-bottom, slot-left-up,
    # top-left, left.
    SL, SR, SD = 6.7, 15.3, 9.3   # slot left/right X, slot depth Y (bottom of slot)
    edge(0, 0, W, 0)          # bottom
    edge(W, 0, W, H)          # right
    edge(W, H, SR, H)         # top-right segment
    edge(SR, H, SR, SD)       # slot right wall (down)
    edge(SR, SD, SL, SD)      # slot bottom
    edge(SL, SD, SL, H)       # slot left wall (up)
    edge(SL, H, 0, H)         # top-left segment
    edge(0, H, 0, 0)          # left

    net_pads = {}
    for ref, lib, entry, x, y, rot, value in COMPONENTS:
        libpath = PRETTY if lib == "custom" else os.path.join(STOCK, lib + ".pretty")
        fp = pcbnew.FootprintLoad(libpath, entry)
        if fp is None:
            raise RuntimeError(f"missing footprint {libpath}:{entry}")
        fp.SetReference(ref); fp.SetValue(value)
        fp.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
        if rot: fp.SetOrientationDegrees(rot)
        board.Add(fp)
        for pad in fp.Pads():
            net = PADNETS.get(ref, {}).get(pad.GetName())
            if net:
                pad.SetNetCode(code(net))
                p = pad.GetPosition()
                net_pads.setdefault(net, []).append((pcbnew.ToMM(p.x), pcbnew.ToMM(p.y)))

    board.Save(OUT)
    print("saved", OUT, "| 22x25mm + top slot X[6.7,15.3] depth->9.3")


if __name__ == "__main__":
    main()
