#!/usr/bin/env python3
"""Post-route: (1) widen thin tracks, (2) drop a GND stitching via at every GND
pad so the B.Cu ground pour connects them (GND is NOT trace-routed -- excluded
from Freerouting via -inc GND -- it connects through the pour + these vias), and
(3) add + fill the B.Cu GND pour (slot-avoiding). Usage: pour_and_fill.py board"""
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
gnd = b.FindNet("GND"); gcode = gnd.GetNetCode()
def mm(v): return pcbnew.FromMM(v)
# derive outline bbox + slot from Edge.Cuts
bb = b.GetBoardEdgesBoundingBox()
W = pcbnew.ToMM(bb.GetWidth()); H = pcbnew.ToMM(bb.GetHeight())
OX = pcbnew.ToMM(bb.GetX()); OY = pcbnew.ToMM(bb.GetY())

# widen thin tracks: GetTracks() internally hits the py3.14 SwigPyIterator bug,
# so walk the raw TRACKS collection by index instead.
trk = b.Tracks()
try:
    ntr = trk.size()
except Exception:
    ntr = len(trk)
for i in range(ntr):
    t = trk[i]
    if isinstance(t, pcbnew.PCB_TRACK) and not isinstance(t, pcbnew.PCB_VIA):
        if t.GetWidth() < mm(0.2): t.SetWidth(mm(0.2))

# GND stitching via at each GND pad
placed = 0
fps = b.GetFootprints()
for fi in range(len(fps)):
    fp = fps[fi]
    pads = fp.Pads()
    for pi in range(len(pads)):
        pad = pads[pi]
        if pad.GetNetCode() != gcode:
            continue
        p = pad.GetPosition()
        dx = mm(0.7) if pad.GetAttribute() == pcbnew.PAD_ATTRIB_SMD else 0
        v = pcbnew.PCB_VIA(b)
        v.SetViaType(pcbnew.VIATYPE_THROUGH)
        v.SetPosition(pcbnew.VECTOR2I(p.x + dx, p.y))
        v.SetDrill(mm(0.3)); v.SetWidth(mm(0.6))
        v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
        v.SetNetCode(gcode)
        b.Add(v)
        # short trace from pad to via on F.Cu so the SMD pad ties to the via
        if dx:
            tr = pcbnew.PCB_TRACK(b)
            tr.SetStart(pcbnew.VECTOR2I(p.x, p.y))
            tr.SetEnd(pcbnew.VECTOR2I(p.x + dx, p.y))
            tr.SetWidth(mm(0.25)); tr.SetLayer(pcbnew.F_Cu); tr.SetNetCode(gcode)
            b.Add(tr)
        placed += 1

# B.Cu GND pour: full-board inset rectangle. KiCad fill respects Edge.Cuts
# (slot cutout) automatically, so no manual slot-avoidance geometry needed.
z = pcbnew.ZONE(b); z.SetLayer(pcbnew.B_Cu); z.SetNet(gnd)
poly = z.Outline(); poly.NewOutline()
for x,y in [(OX+0.3,OY+0.3),(OX+W-0.3,OY+0.3),(OX+W-0.3,OY+H-0.3),(OX+0.3,OY+H-0.3)]:
    poly.Append(pcbnew.VECTOR2I(mm(x), mm(y)))
b.Add(z)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(sys.argv[1])
print(f"placed {placed} GND stitching vias; added+filled B.Cu GND pour")
