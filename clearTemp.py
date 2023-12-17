#!/usr/bin/python3

from argparse import ArgumentParser
import dmenu
import json
import os
import subprocess
import sys
import time
import lib

appDesc = """
send current temp hyprland client [if it exits] back to the
workspace it is originally from
"""

parser = ArgumentParser(description=appDesc)
parser.add_argument(
        '-d',
        '--default',
        default=0,
        help='default workspace to send client if none specified. s => special. c => current. f => fresh. [default s]'
)
args = parser.parse_args()
defaultWS = args.default

clients = lib.getClientsByAddress()
if lib.existsTmp("address") and lib.existsTmp("active"):
    address = lib.slurpTmp("address")
    if not address:
        lib.exit("no temp address found", 1)
    address = address.strip()
    if (address not in clients):
        lib.exit("no temp address found", 1)
    client = clients[address]
    # ws = "special" # defaultWS TODO handle
    ws = lib.slurpTmp("source") or "special"
    ws = ws.strip()
    lib.moveWindow(address, ws)
    os.system(f"rm {lib.tmpdir}/*")
else:
    lib.exit("no temp address found", 1)
