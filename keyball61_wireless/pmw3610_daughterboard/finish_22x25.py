#!/usr/bin/env python3
"""Minimal finishing pass: place a GND stitching via ONLY at the sensor's GND pad
(U1.11) so it ties into the B.Cu pour (fixes starved_thermal). GND is otherwise
trace-routed by Freerouting + closed by the pour. Do NOT carpet-bomb vias.
Usage: finish_22x25.py board"""
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
gnd = b.FindNet("GND"); gc = gnd.GetNetCode()
def mm(v): return pcbnew.FromMM(v)
def add_via(x, y):
    v = pcbnew.PCB_VIA(b); v.SetViaType(pcbnew.VIATYPE_THROUGH)
    v.SetPosition(pcbnew.VECTOR2I(x, y)); v.SetDrill(mm(0.3)); v.SetWidth(mm(0.55))
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNetCode(gc); b.Add(v)

# via only at the two THT GND pads (sensor U1.11 and connector GNDs) — these are
# the multi-layer GND anchors that must reach the B.Cu pour. SMD GND pads are
# already tied by trace routing.
fps = b.GetFootprints(); placed = 0
for fi in range(len(fps)):
    fp = fps[fi]; pads = fp.Pads()
    for pi in range(len(pads)):
        p = pads[pi]
        if p.GetNetCode() == gc and p.GetAttribute() != pcbnew.PAD_ATTRIB_SMD:
            pos = p.GetPosition(); add_via(pos.x, pos.y); placed += 1
            # solid zone connection so the pour ties fully (no starved thermal)
            try: p.SetZoneConnection(pcbnew.ZONE_CONNECTION_FULL)
            except Exception: pass

# guide-post hole (Ø0.9mm NPTH) below the lens slot, added post-route so it does
# not break the Specctra SES round-trip (a netless NPTH footprint fails import)
try:
    fp = pcbnew.FOOTPRINT(b)
    pad = pcbnew.PAD(fp); pad.SetAttribute(pcbnew.PAD_ATTRIB_NPTH)
    pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE); pad.SetSize(pcbnew.VECTOR2I(mm(0.9), mm(0.9)))
    pad.SetDrillSize(pcbnew.VECTOR2I(mm(0.9), mm(0.9)))
    pad.SetPosition(pcbnew.VECTOR2I(mm(11.0), mm(10.15)))
    pad.SetLayerSet(pad.UnplatedHoleMask())
    fp.Add(pad); fp.SetPosition(pcbnew.VECTOR2I(mm(11.0), mm(10.15)))
    fp.SetReference("GP1")
    b.Add(fp)
except Exception as e:
    print("guide-post note:", e)
# fill zones LAST so the pour clears the guide-post hole
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(sys.argv[1])
print(f"added {placed} GND vias at THT GND pads (sensor + connector)")
