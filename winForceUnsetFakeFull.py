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
fakeFullscreen = window["fakeFullscreen"]

if fakeFullscreen:
    os.system(f"hyprctl dispatch fakefullscreen")
else:
    print("already unset")
