#!/usr/bin/env python3
"""Add + fill the B.Cu GND pour with SOLID pad connection (no thermal spokes),
so THT GND pads (sensor U1.11) don't starve. GND is trace-routed by Freerouting;
this pour is the ground plane. Usage: pour_gnd.py board"""
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
gnd = b.FindNet("GND")
def mm(v): return pcbnew.FromMM(v)
bb = b.GetBoardEdgesBoundingBox()
W = pcbnew.ToMM(bb.GetWidth()); H = pcbnew.ToMM(bb.GetHeight())
OX = pcbnew.ToMM(bb.GetX()); OY = pcbnew.ToMM(bb.GetY())
z = pcbnew.ZONE(b); z.SetLayer(pcbnew.B_Cu); z.SetNet(gnd)
# solid connection to pads (no thermal relief) -> no starved thermal
try: z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
except Exception as e: print("padconn note:", e)
p = z.Outline(); p.NewOutline()
for x, y in [(OX+0.3,OY+0.3),(OX+W-0.3,OY+0.3),(OX+W-0.3,OY+H-0.3),(OX+0.3,OY+H-0.3)]:
    p.Append(pcbnew.VECTOR2I(mm(x), mm(y)))
b.Add(z)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(sys.argv[1])
print("poured B.Cu GND (solid pad connection)")
