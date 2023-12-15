#!/usr/bin/python3

from argparse import ArgumentParser
import dmenu
import json
import os
import subprocess
import sys
import time
import urllib.parse
import requests

appDesc = "bring hyprland client from other workspace to current"
parser = ArgumentParser(description=appDesc)
parser.add_argument("cmd", help="tridactyl command to run")
parser.add_argument(
        '-p',
        '--pid',
        default=None,
        help='process id of firefox instance to target')
parser.add_argument(
        '-s',
        '--sid',
        default=None,
        help='session id of firefox instance to target')
args = parser.parse_args()
pid = args.pid
sid = args.sid
cmd = args.cmd

dir_path = os.path.dirname(os.path.realpath(__file__))

def cmdJson(cmd):
    argv = cmd.split(" ")
    result = subprocess.run(argv, stdout=subprocess.PIPE)
    return json.loads(result.stdout.decode())

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

isPid = not sid
iid = sid or pid
if not iid:
    activeWindow = cmdJson('hyprctl activewindow -j')
    if activeWindow["class"] == "firefox":
        iid = activeWindow["pid"]
    clients = cmdJson('hyprctl clients -j')
    for client in clients:
        if client["class"] == "firefox":
            iid = client["pid"]
            break

p1 = "process" if isPid else "session"
endpoint = f"http://localhost:9215/{p1}/{iid}/job"
result = requests.post(endpoint, json = {'run': args.cmd})
print(result.text)
