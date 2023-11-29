#!/usr/bin/python3

from argparse import ArgumentParser
import dmenu
import json
import os
import subprocess
import sys

def cmdJson(cmd):
    argv = cmd.split(" ")
    result = subprocess.run(argv, stdout=subprocess.PIPE)
    return json.loads(result.stdout.decode())

monitors = cmdJson('hyprctl monitors -j')
activeWorkspaceId = int(monitors[0]["activeWorkspace"]["id"])

def getClientData(client):
    address = client["address"]
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
        "class": cclass,
        "title": title
    }

used = {}
for i in range(1, 10):
    used[i] = False
clients = list(map(getClientData, cmdJson('hyprctl clients -j')))
for client in clients:
    used[client["workspaceId"]] = True
fresh = 1
while (fresh < 9):
    if not used[fresh]:
        break
    fresh = fresh + 1
print(fresh)
