#!/usr/bin/python3

from argparse import ArgumentParser
import dmenu
import json
import os
import subprocess
import sys
import time

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

blank = "󰂵"
sepL = blank * 2
sepR = blank * 2

def cmdJson(cmd):
    argv = cmd.split(" ")
    result = subprocess.run(argv, stdout=subprocess.PIPE)
    return json.loads(result.stdout.decode())

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

monitors = cmdJson('hyprctl monitors -j')
activeWorkspaceId = int(monitors[0]["activeWorkspace"]["id"])

def isValidClient(client):
    workspaceId = client["workspace"]["id"]
    workspace = client["workspace"]["name"]
    isSpecial = workspace == "special"
    isActive = workspaceId == activeWorkspaceId
    isVisible = workspaceId > 0
    return ((isVisible and (not hidden_only)) or isSpecial) and (not isActive)

def getClientData(client):
    address = client["address"]
    floating = client["floating"]
    pid = client["pid"]
    workspace = client["workspace"]["name"]
    workspaceId = client["workspace"]["id"]
    if workspace == "special":
        workspace = ""
    cclass = client["class"] or client["initialClass"]
    title = client["title"] or client["initialTitle"] or cclass
    return {
        "address": address,
        "pid": pid,
        "workspace": workspace,
        "workspaceId": workspaceId,
        "floating": floating,
        "class": cclass,
        "title": title
    }

clients = list(map(getClientData, filter(isValidClient, cmdJson('hyprctl clients -j'))))
clients = sorted(clients, key=lambda client: client["workspaceId"])
maxLenClass = 0
maxLenWorkspace = 0
for client in clients:
    cclass    = client["class"]
    workspace = client["workspace"]
    maxLenClass     = max(maxLenClass    , len(cclass   ))
    maxLenWorkspace = max(maxLenWorkspace, len(workspace))

labels = []
ref = {}
print([maxLenClass, maxLenWorkspace])
for client in clients:
    cclass    = strPad(client["class"]    , maxLenClass    )
    workspace = strPad(client["workspace"], maxLenWorkspace)
    title     = client["title"]
    titleLabel = f'{title}' if title != client["class"] else ""
    label = f'{workspace} {blank}{cclass}{blank} {titleLabel}'
    labels.append(label)
    ref[label] = client

if len(labels) <= 0:
    print("no clients on other workspaces")
    sys.exit()

selectedLabel = dmenu.show(
    labels,
    command=f"{dir_path}/rofi-dmenu",
    prompt=f'Summon {"Temp " if temp else ""}Client',
    case_insensitive=True
)

if selectedLabel in ref:
    client = ref[selectedLabel]
    dispatch = "hyprctl dispatch"
    address = client["address"]
    window = f'address:{address}'
    floating = client["floating"]
    shouldFloat = os.path.isfile(f"{dir_path}/state/floating/{address}")
    os.system(f'{dispatch} movetoworkspacesilent {activeWorkspaceId},{window}')
    os.system(f'{dispatch} focuswindow {window}')
    if temp:
        os.system(f"touch {dir_path}/state/temp/{address}")
        if not floating:
            os.system(f'{dispatch} togglefloating {window}')
        os.system(f'{dispatch} resizewindowpixel exact 1000 384,{window}')
        os.system(f'{dispatch} movewindowpixel exact 460 12,{window}')
    elif floating != shouldFloat:
        time.sleep(0.1)
        os.system(f'{dispatch} togglefloating {window}')
