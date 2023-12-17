#!/usr/bin/python3

from argparse import ArgumentParser
import dmenu
import json
import os
import subprocess
import sys
import time
import lib

appDesc = "send hyprland clients from current workspace elsewhere"
parser = ArgumentParser(description=appDesc)
parser.add_argument(
        '-c',
        '--clients-type',
        default=0,
        help= """
clients to include.
0 => just focused. 1 => all. 2 => all but focused.
[default 0]
"""
)

parser.add_argument('-f', '--fresh', action='store_true', help='send to fresh workspace as opposed to hidden')
args = parser.parse_args()
fresh = args.fresh
clients_type = int(args.clients_type)

activeWindow = lib.cmdJson('hyprctl activewindow -j')
activeWorkspaceId = int(activeWindow["workspace"]["id"])
activeAddress = activeWindow["address"]

target_ws = "special"
if fresh:
    target_ws = lib.cmdText(f"{lib.bindir}/getFreshWorkspace.py")

clients = lib.getClients()
for client in clients:
    workspaceId = client["workspaceId"]
    floating = client["floating"]
    pid = client["pid"]
    address = client["address"]
    class_ = client["class"]
    title = client["title"]
    if workspaceId != activeWorkspaceId:
        continue
    if address == activeAddress and clients_type == 2:
        continue
    if address != activeAddress and clients_type == 0:
        continue
    lib.moveWindow(address, target_ws)
