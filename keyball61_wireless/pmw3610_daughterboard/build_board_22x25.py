#!/usr/bin/env python3
"""22x25mm ORIGINAL-SIZE variant. Exact original slot/sensor/connector positions.
All 14 support parts packed front-side into the side columns + the thin bottom
strip below the connector. GND connects via pour + stitching vias (not traces).
Tests whether the original footprint routes now that the iterator bug is fixed."""
import os, pcbnew
HERE = os.path.dirname(os.path.abspath(__file__))
PRETTY = os.path.join(HERE, "pmw3610_kb.pretty")
STOCK = "/usr/share/kicad/footprints"
OUT = os.path.join(HERE, "pmw3610_daughterboard.kicad_pcb")
W, H = 23.0, 25.0
def mm(v): return pcbnew.FromMM(v)
NETS = ["GND","VCC","+1V8","SCLK","SDIO","NCS","MOTION","NRESET","CP","CN","VCP","PASST"]

# ORIGINAL positions (bottom-left origin): sensor columns X5.65/16.35 center Y17.5;
# connector Y5.2. LENS CUTOUT (datasheet LM18-LSI body 12.9 x 8.25mm) drops through
# the board between the pin columns, centered on the sensor optical center.
# Board thickness = 1.0mm (set post-build via text patch). Guide-post holes Ø0.9mm.
# Cutout: width 8.25 (X, between columns 5.65<->16.35), length 12.9 (Y), centered (11,17.5).
LENS_W, LENS_L = 8.25, 12.9
LCX, LCY = 11.0, 17.5
SL, SR = LCX-LENS_W/2, LCX+LENS_W/2      # 6.875, 15.125
SB, ST = LCY-LENS_L/2, LCY+LENS_L/2      # 11.05, 23.95  (interior cutout, not open to edge)
SENS_X, SENS_Y = 11.0, 17.0
CONN_Y = 5.2
U1_NETS = {"2":"SDIO","3":"SCLK","5":"NCS","6":"VCC","7":"NRESET","8":"MOTION",
           "9":"VCP","10":"PASST","11":"GND","12":"CP","13":"CN","14":"+1V8"}
CONN_NET = {"1":"SCLK","2":"SDIO","3":"GND","4":"VCC","5":"GND","6":"NCS","7":"NRESET"}

# ALL support parts ABOVE the connector (Y>5.5) so NOTHING sits below the connector
# line where it would foul the main board at the 90-degree joint. Parts live in the
# left column (X~3) and right column (X~19.5), flanking the lens slot + sensor.
SUPPORT = [
    # RULE-BASED (IPC/Eurocircuits): 0603 pitch >=2.7mm, 0805 >=3.2mm, edge gap >=0.25mm.
    # Front top-side: sensor + LDO + charge-pump/decoupling caps that must hug pins.
    # Bulk 0805s (C1,C6) and DNP R2 pushed to BACK layer to relieve front density.
    #
    # LEFT column (X~2.8), 0603 @ 2.8mm pitch, U2 (LDO) at far bottom
    # LEFT column caps stacked HIGH (Y 12-24, beside U1 left pins); U2 in the
    # U1-free bottom band (Y~8.5, below U1's pin columns, above the connector).
    ("C4","Capacitor_SMD","C_0603_1608Metric", 2.8, 12.5, 90, "100nF","F"),   # VDD bulk
    ("R1","Resistor_SMD","R_0603_1608Metric",  2.8, 15.5, 90, "10k","F"),     # NRESET pull
    ("C9","Capacitor_SMD","C_0603_1608Metric", 2.8, 18.5, 90, "1uF","F"),     # LDO in
    ("C8","Capacitor_SMD","C_0603_1608Metric", 2.8, 21.5, 90, "1uF","F"),     # LDO out
    ("U2","Package_TO_SOT_SMD","SOT-23-5",     4.5, 8.3,  0,  "TLV74318PDBVR","F"),  # LDO in bottom band, clear of U1
    # RIGHT column (X~20.3), 0603 @ 3.0mm pitch; charge-pump/analog caps hug sensor
    ("C3","Capacitor_SMD","C_0603_1608Metric", 20.3, 8.0,  90, "100nF","F"),   # VDDIO decouple
    ("C5","Capacitor_SMD","C_0603_1608Metric", 20.3, 11.5, 90, "10nF","F"),    # CP-CN, hugs U1.12/13
    ("C7","Capacitor_SMD","C_0603_1608Metric", 20.3, 15.0, 90, "10nF","F"),    # VCP, hugs U1.9
    ("C2","Capacitor_SMD","C_0603_1608Metric", 20.3, 18.5, 90, "100nF","F"),   # +1V8 decouple
    # BACK side (under the pins): bulk 0805s + DNP MOTION pull-up. Above connector,
    # so they don't foul the 90-degree main-board joint. Back-side = shortest loop.
    ("C1","Capacitor_SMD","C_0805_2012Metric", 9.0,  7.5, 0, "3.3uF","F"),   # +1V8 bulk, band below sensor pins
    ("C6","Capacitor_SMD","C_0805_2012Metric", 13.0, 7.5, 0, "10uF","F"),    # PASST bulk, band below sensor pins
    ("R2","Resistor_SMD","R_0603_1608Metric",  16.0, 7.5, 0, "10k","F"),      # MOTION pull(DNP)
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
    ds.m_MinThroughDrill=mm(0.3); ds.m_ViasMinSize=mm(0.5)
    ds.m_CopperEdgeClearance=mm(0.15)
    try: ds.SetBoardThickness(mm(1.0))   # datasheet/ufan: 1.0mm for ball-facing PMW3610
    except Exception as e: print("thick note:", e)
    try:
        sev=ds.m_DRCSeverities; sev["courtyards_overlap"]=pcbnew.SEVERITY_IGNORE
    except Exception as e: print("sev",e)
    try:
        d=board.GetAllNetClasses().get("Default")
        if d: d.SetTrackWidth(mm(0.2)); d.SetViaDiameter(mm(0.5)); d.SetViaDrill(mm(0.3)); d.SetClearance(mm(0.15))
    except Exception as e: print("nc",e)
    def code(n): return board.FindNet(n).GetNetCode()
    def edge(x0,y0,x1,y1):
        s=pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(pcbnew.VECTOR2I(mm(x0),mm(y0))); s.SetEnd(pcbnew.VECTOR2I(mm(x1),mm(y1)))
        s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(mm(0.1)); board.Add(s)
    # full outline with a top-OPEN lens slot (sized to LM18-LSI body, opens toward
    # the ball at the top edge). Open slot leaves the routing channel usable, unlike
    # a fully-enclosed hole -- this is what the original Keyball board does.
    edge(0,0,W,0); edge(W,0,W,H)          # bottom, right
    edge(W,H,SR,H)                         # top-right segment (to slot right wall)
    edge(SR,H,SR,SB)                       # slot right wall down
    edge(SR,SB,SL,SB)                      # slot bottom
    edge(SL,SB,SL,H)                       # slot left wall up
    edge(SL,H,0,H)                         # top-left segment
    edge(0,H,0,0)                          # left
    # guide-post hole (Ø0.9mm NPTH) below the slot on the optical axis
    def npth(x,y,d=0.9):
        fp=pcbnew.FOOTPRINT(board)
        pad=pcbnew.PAD(fp); pad.SetAttribute(pcbnew.PAD_ATTRIB_NPTH)
        pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE); pad.SetSize(pcbnew.VECTOR2I(mm(d),mm(d)))
        pad.SetDrillSize(pcbnew.VECTOR2I(mm(d),mm(d)))
        pad.SetPosition(pcbnew.VECTOR2I(mm(x),mm(y)))
        pad.SetLayerSet(pad.UnplatedHoleMask())
        fp.Add(pad); fp.SetPosition(pcbnew.VECTOR2I(mm(x),mm(y)))
        board.Add(fp)
    #npth(LCX, SB-0.9)   # guide post just below the slot
    def place(ref,libpath,entry,x,y,rot,value,padnets=None,back=False):
        fp=pcbnew.FootprintLoad(libpath,entry)
        if fp is None: raise RuntimeError(f"missing {libpath}:{entry}")
        fp.SetReference(ref); fp.SetValue(value)
        fp.SetPosition(pcbnew.VECTOR2I(mm(x),mm(y)))
        if rot: fp.SetOrientationDegrees(rot)
        if back: fp.Flip(fp.GetPosition(), False)
        board.Add(fp)
        gi=fp.GraphicalItems()
        for k in range(len(gi)):
            if gi[k].GetLayer()==pcbnew.Edge_Cuts: gi[k].SetLayer(pcbnew.Dwgs_User)
        for pad in fp.Pads():
            net=(padnets or {}).get(pad.GetName())
            if net: pad.SetNetCode(code(net))
    place("U1", PRETTY, "PMW3610DM-SUDU-siderakb", SENS_X, SENS_Y, 90, "PMW3610DM-SUDU", U1_NETS)
    place("J1", PRETTY, "Conn_Keyball_7pin_stock", 11.0, CONN_Y, 0, "Conn_Keyball_7pin", CONN_NET)
    # separate MOTION solder pad near U1 pin8 (top-right area) for the wire
    place("MOT1", PRETTY, "MOTION_solder_pad", 21.16, 5.2, 0, "MOTION", {"1":"MOTION"})
    for ref,lib,entry,x,y,rot,value,side in SUPPORT:
        place(ref, os.path.join(STOCK,lib+".pretty"), entry, x, y, rot, value, SUP_NETS.get(ref), back=(side=="B"))
    board.Save(OUT)
    print(f"saved {OUT} | 22x25 1.0mm, lens cutout X[{SL:.2f},{SR:.2f}] Y[{SB:.2f},{ST:.2f}], sensor({SENS_X},{SENS_Y}) conn Y={CONN_Y}")

if __name__ == "__main__":
    main()
