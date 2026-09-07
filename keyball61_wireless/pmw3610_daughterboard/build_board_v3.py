#!/usr/bin/env python3
"""
PMW3610 Keyball daughterboard, pcbnew build.

Board grown to 24 x 32 mm from the original 22 x 25: +1mm each side (X margin),
+7mm below the connector (support-part room). The OPTICS-CRITICAL features keep
their ORIGINAL positions relative to the TOP (ball) edge, so the sensor still
hits the ball at the correct angle and the top of the board seats in the housing
as before; the growth is on the non-optical sides/bottom.

Coordinate system: bottom-left origin, Y up. Top edge = Y=32 (=H).
Original 22x25 features were referenced from the top; we preserve top-distance:
  new_Y = H - (25 - old_Y_from_bottom).
X features shift +1.0 (left margin added).

Original (22x25, from bottom):
  slot X[6.7,15.3] from top down to Y=9.3 (=15.7 below top)
  sensor pin columns X=5.65 / 16.35, center Y=17.3
  connector row Y=5.2
Shifted to 24x32 (X+1, top-preserved):
  slot X[7.7,16.3], from top (Y=32) down to Y=16.3
  sensor columns X=6.65 / 17.35, center Y=24.3
  connector row Y=12.2
  support parts: Y 0.5..11 (the new 7mm band below connector) + sides.
"""
import os, pcbnew
HERE = os.path.dirname(os.path.abspath(__file__))
PRETTY = os.path.join(HERE, "pmw3610_kb.pretty")
STOCK = "/usr/share/kicad/footprints"
OUT = os.path.join(HERE, "pmw3610_daughterboard.kicad_pcb")
W, H = 24.0, 32.0
def mm(v): return pcbnew.FromMM(v)

NETS = ["GND","VCC","+1V8","SCLK","SDIO","NCS","MOTION","NRESET","CP","CN","VCP","PASST"]

# slot / sensor / connector (24x32 coords, top-preserved)
SL, SR = 7.7, 16.3          # slot X walls
SD = 16.3                    # slot bottom Y (15.7 below top edge 32)
SENS_X, SENS_Y = 12.0, 24.0  # sensor footprint center (rot 90 -> rows at X 6.65/17.35)
CONN_Y = 12.2                # connector row

U1_NETS = {"2":"SDIO","3":"SCLK","5":"NCS","6":"VCC","7":"NRESET","8":"MOTION",
           "9":"VCP","10":"PASST","11":"GND","12":"CP","13":"CN","14":"+1V8"}
CONN_NET = {"1":"SCLK","2":"SDIO","3":"GND","4":"VCC","5":"GND","6":"NCS",
            "7":"NRESET","8":"MOTION"}

# All support parts FRONT side (badjeff pattern). Charge-pump caps in the side
# columns beside the sensor; LDO+bulk+IO in the roomy band below the connector
# (Y 1..10). Board center X=12.
SUPPORT = [
    # side columns beside sensor (X<6.65 left, X>17.35 right), analog caps hug pins
    ("C5","Capacitor_SMD","C_0603_1608Metric", 3.5, 20.0, 90, "10nF","F"),   # CP-CN
    ("C4","Capacitor_SMD","C_0603_1608Metric", 3.5, 23.0, 90, "100nF","F"),  # VDD bulk
    ("C6","Capacitor_SMD","C_0805_2012Metric", 20.5,20.5, 90, "10uF","F"),   # PASST
    ("C2","Capacitor_SMD","C_0603_1608Metric", 20.5,24.0, 90, "100nF","F"),  # +1V8
    ("C7","Capacitor_SMD","C_0603_1608Metric", 20.5,28.0, 90, "10nF","F"),   # VCP, right side near U1.9
    ("R1","Resistor_SMD","R_0603_1608Metric",  3.5, 26.5, 90, "10k","F"),    # NRESET pull, left
    # roomy band below connector (Y 1..10): LDO + IO + bulk + more
    ("U2","Package_TO_SOT_SMD","SOT-23-5",     4.0, 8.5, 0,  "TLV74318PDBVR","F"),
    ("C8","Capacitor_SMD","C_0603_1608Metric", 9.0, 8.5, 0,  "1uF","F"),
    ("C9","Capacitor_SMD","C_0603_1608Metric", 13.0,8.5, 0,  "1uF","F"),
    ("C1","Capacitor_SMD","C_0805_2012Metric", 17.5,8.5, 0,  "3.3uF","F"),
    ("C3","Capacitor_SMD","C_0603_1608Metric", 21.0,8.5, 0,  "100nF","F"),
    ("R2","Resistor_SMD","R_0603_1608Metric",  6.0, 4.5, 0,  "10k","F"),     # MOTION pull(DNP)
]
SUP_NETS = {
    "U2":{"1":"VCC","2":"GND","3":"VCC","5":"+1V8"},
    "C8":{"1":"VCC","2":"GND"}, "C9":{"1":"+1V8","2":"GND"},
    "C1":{"1":"+1V8","2":"GND"},"C3":{"1":"VCC","2":"GND"},
    "C2":{"1":"+1V8","2":"GND"},"C5":{"1":"CP","2":"CN"},
    "C6":{"1":"PASST","2":"GND"},"C7":{"1":"VCP","2":"GND"},
    "C4":{"1":"+1V8","2":"GND"},"R1":{"1":"VCC","2":"NRESET"},
    "R2":{"1":"VCC","2":"MOTION"},
}


def main():
    board = pcbnew.BOARD()
    for n in NETS:
        if board.FindNet(n) is None: board.Add(pcbnew.NETINFO_ITEM(board, n))
    ds = board.GetDesignSettings()
    ds.m_TrackMinWidth=mm(0.15); ds.m_MinClearance=mm(0.15)
    ds.m_MinThroughDrill=mm(0.3); ds.m_ViasMinSize=mm(0.6)
    ds.m_CopperEdgeClearance=mm(0.25)
    try:
        sev=ds.m_DRCSeverities
        sev["courtyards_overlap"]=pcbnew.SEVERITY_IGNORE
    except Exception as e: print("sev",e)
    try:
        d=board.GetAllNetClasses().get("Default")
        if d:
            d.SetTrackWidth(mm(0.2)); d.SetViaDiameter(mm(0.6)); d.SetViaDrill(mm(0.3)); d.SetClearance(mm(0.15))
    except Exception as e: print("nc",e)
    def code(n): return board.FindNet(n).GetNetCode()

    def edge(x0,y0,x1,y1):
        s=pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(pcbnew.VECTOR2I(mm(x0),mm(y0))); s.SetEnd(pcbnew.VECTOR2I(mm(x1),mm(y1)))
        s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(mm(0.1)); board.Add(s)
    edge(0,0,W,0); edge(W,0,W,H); edge(W,H,SR,H); edge(SR,H,SR,SD)
    edge(SR,SD,SL,SD); edge(SL,SD,SL,H); edge(SL,H,0,H); edge(0,H,0,0)

    def place(ref,libpath,entry,x,y,rot,value,back=False,padnets=None):
        fp=pcbnew.FootprintLoad(libpath,entry)
        if fp is None: raise RuntimeError(f"missing {libpath}:{entry}")
        fp.SetReference(ref); fp.SetValue(value)
        fp.SetPosition(pcbnew.VECTOR2I(mm(x),mm(y)))
        if rot: fp.SetOrientationDegrees(rot)
        if back: fp.Flip(fp.GetPosition(), False)
        board.Add(fp)
        # strip any Edge.Cuts graphics the source footprint carries (index-safe)
        gi = fp.GraphicalItems()
        for k in range(len(gi)):
            g = gi[k]
            if g.GetLayer() == pcbnew.Edge_Cuts:
                g.SetLayer(pcbnew.Dwgs_User)
        for pad in fp.Pads():
            net=(padnets or {}).get(pad.GetName())
            if net: pad.SetNetCode(code(net))

    place("U1", PRETTY, "PMW3610DM-SUDU-siderakb", SENS_X, SENS_Y, 90, "PMW3610DM-SUDU", padnets=U1_NETS)
    place("J1", PRETTY, "Conn_Keyball_8pin_v2", 12.0, CONN_Y, 0, "Conn_Keyball_8pin", padnets=CONN_NET)
    for ref,lib,entry,x,y,rot,value,side in SUPPORT:
        place(ref, os.path.join(STOCK,lib+".pretty"), entry, x, y, rot, value,
              back=(side=="B"), padnets=SUP_NETS.get(ref))

    board.Save(OUT)
    print(f"saved {OUT} | 24x32, slot X[{SL},{SR}]->{SD}, sensor({SENS_X},{SENS_Y}) conn Y={CONN_Y}")


if __name__ == "__main__":
    main()
