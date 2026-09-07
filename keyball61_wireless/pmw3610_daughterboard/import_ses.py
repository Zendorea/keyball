#!/usr/bin/env python3
"""Import a Freerouting Specctra .ses into a board and save. Usage: import_ses.py board.kicad_pcb routed.ses"""
import sys, pcbnew
pcb, ses = sys.argv[1], sys.argv[2]
board = pcbnew.LoadBoard(pcb)
ok = pcbnew.ImportSpecctraSES(board, ses)
if ok:
    board.Save(pcb)
print("SES import", "OK" if ok else "FAILED", "->", pcb)
sys.exit(0 if ok else 1)
