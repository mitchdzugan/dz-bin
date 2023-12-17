#!/usr/bin/python3

from argparse import ArgumentParser
import dmenu
import json
import os
import subprocess
import sys
import time
import lib

appDesc = "bring hyprland client from other workspace to current"
parser = ArgumentParser(description=appDesc)
parser.add_argument(
        '-t',
        '--temp',
        action='store_true',
        help='bring temporarily. will float in center screen')
parser.add_argument(
        '-ho',
        '--hidden-only',
        action='store_true',
        help='only include clients from hidden workspace')
args = parser.parse_args()
hidden_only = args.hidden_only
temp = args.temp

dir_path = os.path.dirname(os.path.realpath(__file__))

sep = " 󱤩 "
sepL = sep
sepR = sep

blank = " "
sepL = blank * 2
sepR = blank * 2

def strPad(s, atLeast):
    toPad = atLeast - len(s)
    if toPad <= 0:
        return s
    padLeft  = int(toPad / 2)
    padRight = toPad - padLeft
    blank
    left  = blank * padLeft
    right = blank * padRight
    return f"{left}{s}{right}"

monitors = lib.cmdJson('hyprctl monitors -j')
activeWorkspaceId = int(monitors[0]["activeWorkspace"]["id"])

def isValidClient(client):
    isSpecial = client["workspaceId"] == -99
    workspaceId = int(client["workspaceId"])
    isActive = workspaceId == activeWorkspaceId
    isVisible = workspaceId > 0
    return ((isVisible and (not hidden_only)) or isSpecial) and (not isActive)

mruLookup = {}
mruAddresses = lib \
    .cmdsPipe(["ls", "-lt", f"{lib.statedir}/active"], ["awk", "{print $9}"]) \
    .strip() \
    .split("\n")
for nth, address in enumerate(mruAddresses):
    mruLookup[address] = float(nth + 1)

print(mruLookup)

def getSortVal(client):
    mruFactor = 0
    if client["address"] in mruLookup:
        mruFactor = 1.0 / mruLookup[client["address"]]
    return float(client["workspaceId"]) - mruFactor

clients = list(filter(isValidClient, lib.getClients()))
clients = sorted(clients, key=getSortVal)
maxLenClass = 0
maxLenWorkspace = 0
for client in clients:
    cclass    = client["class"]
    workspace = client["workspace"]
    maxLenClass     = max(maxLenClass    , len(cclass   ))
    maxLenWorkspace = max(maxLenWorkspace, len(workspace))

labels = []
ref = {}
for client in clients:
    cclass    = strPad(client["class"]    , maxLenClass    )
    workspace = strPad(client["workspace"], maxLenWorkspace)
    title     = client["title"]
    titleLabel = f'{title}' if title != client["class"] else ""
    label = f'{workspace} {blank}{cclass}{blank} {titleLabel}'
    labels.append(label)
    ref[label] = client

if len(labels) <= 0:
    lib.exit("no clients on other workspaces")

selectedLabel = dmenu.show(
    labels,
    command=f"{dir_path}/rofi-dmenu",
    prompt=f'Summon {"Temp " if temp else ""}Client',
    case_insensitive=True
)

if selectedLabel in ref:
    address = ref[selectedLabel]["address"]
    if temp:
        os.system(f"{dir_path}/toTempWindow.py -a {address}")
    else:
        lib.moveWindow(address, activeWorkspaceId)
