#!/usr/bin/python3

from argparse import ArgumentParser
import dmenu
import json
import os
import subprocess
import sys
import time

appDesc = "send hyprland clients from current workspace elsewhere"
parser = ArgumentParser(description=appDesc)
parser.add_argument('-c', '--clients-type', default=0, help='clients to include. 0 => just focused. 1 => all. 2 => all but focused.')
parser.add_argument('-f', '--fresh', action='store_true', help='send to fresh workspace as opposed to hidden')
args = parser.parse_args()
fresh = args.fresh
clients_type = int(args.clients_type)

dir_path = os.path.dirname(os.path.realpath(__file__))

def cmdText(cmd):
    argv = cmd.split(" ")
    result = subprocess.run(argv, stdout=subprocess.PIPE)
    return result.stdout.decode().strip()

def cmdJson(cmd):
    return json.loads(cmdText(cmd))

activeWindow = cmdJson('hyprctl activewindow -j')
activeWorkspaceId = int(activeWindow["workspace"]["id"])
activeAddress = activeWindow["address"]

def getClientData(client):
    address = client["address"]
    pid = client["pid"]
    floating = client["floating"]
    workspace = client["workspace"]["name"]
    workspaceId = client["workspace"]["id"]
    if workspace == "special":
        workspace = ""
    cclass = client["class"] or client["initialClass"]
    title = client["title"] or client["initialTitle"] or cclass
    return {
        "address": address,
        "pid": pid,
        "floating": floating,
        "workspace": workspace,
        "workspaceId": workspaceId,
        "class": cclass,
        "title": title
    }

target_ws = "special"
if fresh:
    target_ws = cmdText(f"{dir_path}/getFreshWorkspace.py")

clients = list(map(getClientData, cmdJson('hyprctl clients -j')))
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
    dispatch = "hyprctl dispatch"
    window = f'pid:{pid}'
    wasTemp = os.path.isfile(f"{dir_path}/state/temp/{pid}")
    os.system(f"rm {dir_path}/state/temp/{pid}")
    if target_ws == "special":
        if floating:
            if not wasTemp:
                os.system(f"touch {dir_path}/state/floating/{pid}")
        else:
            if not wasTemp:
                os.system(f"rm {dir_path}/state/floating/{pid}")
            os.system(f'{dispatch} togglefloating {window}')
            os.system(f'{dispatch} resizewindowpixel exact 1000 384,{window}')
            os.system(f'{dispatch} movewindowpixel exact 460 12,{window}')
            time.sleep(0.5)
    os.system(f'{dispatch} movetoworkspacesilent {target_ws},{window}')
