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
set hyprland client as temp floating window.
  [returns to previous position upon losing focus]
""".strip()

parser = ArgumentParser(description=appDesc)
parser.add_argument(
        '-a',
        '--address',
        help='the client address to make temp. default to focused client')
args = parser.parse_args()
targetAddress = args.address

active = lib.cmdJson('hyprctl activeworkspace -j')
activeWorkspaceId = active["id"]
if (not targetAddress):
    targetAddress = active["lastwindow"]

clients = lib.getClientsByAddress()
if targetAddress in clients:
    client = clients[targetAddress]
    dispatch = "hyprctl dispatch"
    address = client["address"]
    window = f'address:{address}'
    floating = client["floating"]
    source = client["workspace"]
    fromSpecial = False
    if (client["workspaceId"] == -99):
        source = "special"
        fromSpecial = True
    lib.setFloatData(address)
    lib.hyprctl(f'movetoworkspacesilent {activeWorkspaceId},{window}')
    os.system(f"echo {address} > {lib.tmpdir}/address")
    os.system(f"echo {source} > {lib.tmpdir}/source")
    if not floating:
        lib.hyprctl(f'togglefloating {window}')
    lib.hyprctl(f'resizewindowpixel exact 1000 384,{window}')
    lib.hyprctl(f'movewindowpixel exact 460 12,{window}')
    lib.hyprctl(f'focuswindow {window}')
