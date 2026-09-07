#!/usr/bin/env python3
"""Widen thin tracks to 0.25mm. Works around the py3.14 SwigPyIterator bug by
using the collection's C++ indexing rather than Python iteration.
Usage: fix_track_width.py board.kicad_pcb"""
import sys, pcbnew
MIN = pcbnew.FromMM(0.25)
b = pcbnew.LoadBoard(sys.argv[1])

tracks = b.Tracks()            # DRAWINGS/TRACKS collection
# It supports GetCount()+GetItem, or len()+index. Probe both defensively.
def as_list(coll):
    try:
        return [coll[i] for i in range(len(coll))]
    except Exception:
        pass
    try:
        return [coll.GetItem(i) for i in range(coll.GetCount())]
    except Exception:
        pass
    # last resort: CastTo not needed; use board.GetTracks via swig list() alt
    out = []
    it = coll.begin()
    end = coll.end()
    while it != end:
        out.append(it.value() if hasattr(it, "value") else it.__ref__())
        it = it.next() if hasattr(it, "next") else it.__next__()
    return out

n = 0
for t in as_list(tracks):
    if isinstance(t, pcbnew.PCB_VIA):
        continue
    if isinstance(t, pcbnew.PCB_TRACK) and t.GetWidth() < MIN:
        t.SetWidth(MIN)
        n += 1

try:
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
except Exception as e:
    print("zone fill note:", e)
b.Save(sys.argv[1])
print(f"widened {n} tracks to 0.25mm")
