#!/usr/bin/python3

from argparse import ArgumentParser
import dmenu
import json
import os
import subprocess
import sys
import time

dir_path = os.path.dirname(os.path.realpath(__file__))

def cmdJson(cmd):
    argv = cmd.split(" ")
    result = subprocess.run(argv, stdout=subprocess.PIPE)
    return json.loads(result.stdout.decode())

window = cmdJson('hyprctl activewindow -j')
address = window["address"]
floating = window["floating"]
fullscreen = window["fullscreen"]
fullscreenMode = window["fullscreenMode"]

target = f'address:{address}'

if fullscreen:
    if fullscreenMode == 0:
        os.system('hyprctl --batch "dispatch fullscreen ; dispatch fullscreen 1"')
    else:
        os.system(f"hyprctl dispatch fullscreen")
elif floating:
    os.system(f"hyprctl dispatch togglefloating")
else:
    print("lowest")
