#!/usr/bin/env python3
"""
Place-and-net the PMW3610 daughterboard with KiCad pcbnew (native 10.x). NO
hand-routing: Freerouting does the tracks from the exported .dsn. This script
only PLACES footprints with generous spacing (so courtyards/solder-mask do not
overlap), assigns nets, and draws the board outline.

Run:  /usr/bin/python3 build_board.py
"""
import os, pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
PRETTY = os.path.join(HERE, "pmw3610_kb.pretty")
STOCK = "/usr/share/kicad/footprints"
OUT = os.path.join(HERE, "pmw3610_daughterboard.kicad_pcb")
W, H = 34.0, 40.0   # roomier board; U1 is a large 16-DIP so give clearance. still << 100mm

def mm(v): return pcbnew.FromMM(v)

NETS = ["GND", "+3V3", "+1V8", "SCLK", "SDIO", "NCS", "MOTION",
        "NRESET", "CP", "CN", "VCP", "PASST"]

# U1 sensor spans ~ X[center-6, center+6] Y[center-9.6, center+9.6]. Placed at
# (17,12) it occupies X[11,23] Y[2.4,21.6]. Keep ALL other parts out of that box:
# analog caps sit just outside U1 left/right edges at its own Y; everything else
# lives in the lower band Y>=25 with generous spacing.
COMPONENTS = [
    ("U1", "custom", "PMW3610DM-SUDU",            17.0, 12.0, 0,   "PMW3610DM-SUDU"),
    ("J1", "custom", "Conn_Keyball_8pin",         17.0, 37.5, 0,   "Conn_Keyball_8pin"),
    # analog charge-pump caps: just OUTSIDE U1's pad columns (U1 left edge ~11, right ~23)
    ("C7", "Capacitor_SMD", "C_0603_1608Metric",   7.5, 10.0, 90,  "10nF"),   # VCP, left of U1
    ("C5", "Capacitor_SMD", "C_0603_1608Metric",  26.5, 10.0, 90,  "10nF"),   # CP-CN, right of U1
    ("C6", "Capacitor_SMD", "C_0805_2012Metric",  27.5, 14.0, 90,  "10uF"),   # PASST, right of U1
    ("C4", "Capacitor_SMD", "C_0603_1608Metric",   7.5, 14.0, 90,  "100nF"),  # VDD bulk, left of U1
    # lower band (Y>=26), well clear of U1 and spaced apart
    ("U2", "Package_TO_SOT_SMD", "SOT-23-5",       6.0, 27.0, 0,   "TLV74318PDBVR"),
    ("C8", "Capacitor_SMD", "C_0603_1608Metric",  11.0, 27.0, 0,   "1uF"),    # LDO IN
    ("C9", "Capacitor_SMD", "C_0603_1608Metric",  15.0, 27.0, 0,   "1uF"),    # LDO OUT
    ("C1", "Capacitor_SMD", "C_0805_2012Metric",  19.0, 27.0, 0,   "3.3uF"),  # +1V8 bulk
    ("C2", "Capacitor_SMD", "C_0603_1608Metric",  23.0, 27.0, 0,   "100nF"),  # +1V8 decouple
    ("C3", "Capacitor_SMD", "C_0603_1608Metric",  27.0, 27.0, 0,   "100nF"),  # +3V3 decouple
    ("R1", "Resistor_SMD", "R_0603_1608Metric",   30.5, 26.0, 90,  "10k"),    # NRESET pull-up
    ("R2", "Resistor_SMD", "R_0603_1608Metric",   30.5, 30.0, 90,  "10k"),    # MOTION pull-up (DNP)
]

PADNETS = {
    "U1": {"2":"SDIO","3":"SCLK","5":"NCS","6":"+3V3","7":"NRESET","8":"MOTION",
           "9":"VCP","10":"PASST","11":"GND","12":"CP","13":"CN","14":"+1V8"},
    "J1": {"1":"+3V3","2":"GND","3":"SCLK","4":"SDIO","5":"NCS","6":"MOTION","7":"GND"},
    "U2": {"1":"+3V3","2":"GND","3":"+3V3","5":"+1V8"},
    "C1": {"1":"+1V8","2":"GND"}, "C2": {"1":"+1V8","2":"GND"},
    "C3": {"1":"+3V3","2":"GND"}, "C4": {"1":"+1V8","2":"GND"},
    "C5": {"1":"CP","2":"CN"},    "C6": {"1":"PASST","2":"GND"},
    "C7": {"1":"VCP","2":"GND"},  "C8": {"1":"+3V3","2":"GND"},
    "C9": {"1":"+1V8","2":"GND"}, "R1": {"1":"+3V3","2":"NRESET"},
    "R2": {"1":"+3V3","2":"MOTION"},
}


def main():
    board = pcbnew.BOARD()
    for name in NETS:
        if board.FindNet(name) is None:
            board.Add(pcbnew.NETINFO_ITEM(board, name))

    # design rules: min track 0.2mm (< Freerouting's 0.25 default), min clearance 0.2mm,
    # min drill 0.3mm — all within JLCPCB/PCBway 2-layer capability.
    ds = board.GetDesignSettings()
    ds.m_TrackMinWidth = mm(0.2)
    ds.m_MinClearance = mm(0.2)
    ds.m_MinThroughDrill = mm(0.3)
    ds.m_ViasMinSize = mm(0.6)
    # default netclass track/via width
    try:
        ncs = board.GetAllNetClasses()
        default = ncs.get("Default")
        if default is not None:
            default.SetTrackWidth(mm(0.25))
            default.SetViaDiameter(mm(0.6))
            default.SetViaDrill(mm(0.3))
            default.SetClearance(mm(0.2))
    except Exception as e:
        print("netclass note:", e)

    def code(n): return board.FindNet(n).GetNetCode()

    pts = [(0,0),(W,0),(W,H),(0,H),(0,0)]
    for i in range(len(pts)-1):
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetStart(pcbnew.VECTOR2I(mm(pts[i][0]), mm(pts[i][1])))
        seg.SetEnd(pcbnew.VECTOR2I(mm(pts[i+1][0]), mm(pts[i+1][1])))
        seg.SetLayer(pcbnew.Edge_Cuts); seg.SetWidth(mm(0.1))
        board.Add(seg)

    for ref, lib, entry, x, y, rot, value in COMPONENTS:
        libpath = PRETTY if lib == "custom" else os.path.join(STOCK, lib + ".pretty")
        fp = pcbnew.FootprintLoad(libpath, entry)
        if fp is None:
            raise RuntimeError(f"footprint not found: {libpath}:{entry}")
        fp.SetReference(ref); fp.SetValue(value)
        fp.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
        if rot: fp.SetOrientationDegrees(rot)
        board.Add(fp)
        for pad in fp.Pads():
            net = PADNETS.get(ref, {}).get(pad.GetName())
            if net: pad.SetNetCode(code(net))

    board.Save(OUT)
    print("saved", OUT)


if __name__ == "__main__":
    main()
