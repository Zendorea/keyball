#!/usr/bin/env python3
"""Export a KiCad board to Specctra .dsn via pcbnew. Usage: export_dsn.py board.kicad_pcb out.dsn"""
import sys, pcbnew
board = pcbnew.LoadBoard(sys.argv[1])
ok = pcbnew.ExportSpecctraDSN(board, sys.argv[2])
print("DSN export", "OK" if ok else "FAILED", "->", sys.argv[2])
sys.exit(0 if ok else 1)
