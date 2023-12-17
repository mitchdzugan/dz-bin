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
        '-m',
        '--mode',
        default='c',
        help='c => cycle | s => set | m => max | u => unset  [default t]'
)
parser.add_argument(
        '-a',
        '--address',
        default=None,
        help='wayland address of firefox session to target. default focused'
)
args = parser.parse_args()
address = args.address
mode = args.mode
if (address == None):
    address = lib.cmdJson('hyprctl activewindow -j')["address"]
print(address)

class MaxMiddleware:
    def __init__(self): pass
    def pre_set(self, client): pass
    def post_set(self, client): pass
    def pre_unset(self, client): pass
    def post_unset(self, client): pass

class FirefoxMiddleware(MaxMiddleware):
    def post_set(self, client):
        os.system(f'{lib.bindir}/firefoxctrl.py fs_set')
    def pre_unset(self, client):
        os.system(f'{lib.bindir}/firefoxctrl.py fs_unset')

middlewareByClass = {}
middlewareByClass["firefox"] = FirefoxMiddleware()

def getMiddleware(client):
    if client["class"] in middlewareByClass:
        return middlewareByClass[client["class"]]
    return MaxMiddleware()

def fs_set(andMax=False):
    client = lib.getClient(address)
    mw = getMiddleware(client)
    lib.hyprctl('pseudo')
    mw.pre_set(client)
    if not client['fakeFullscreen']:
        lib.hyprctl('fakefullscreen')
    mw.post_set(client)
    if andMax:
        lib.setFloatData(address)
        if not client["floating"]:
            lib.hyprctl('togglefloating')
        lib.maximizeFakeFullscreen(address)
    time.sleep(1)
    lib.hyprctl('pseudo')

def fs_unset():
    client = lib.getClient(address)
    mw = getMiddleware(client)
    lib.hyprctl('pseudo')
    mw.pre_unset(client)
    if client['fakeFullscreen']:
        if lib.isMaxFakeFullscreen(address):
            lib.restoreMaximizedFakeFullscreen(address)
        lib.hyprctl('fakefullscreen')
    mw.post_unset(client)
    time.sleep(1)
    lib.hyprctl('pseudo')

def fs_cycle():
    client = lib.getClient(address)
    if client["fakeFullscreen"] and lib.isMaxFakeFullscreen(address):
        fs_unset()
    else:
        fs_set(client["fakeFullscreen"])

def fs_max():
    client = lib.getClient(address)
    if client["fakeFullscreen"] and lib.isMaxFakeFullscreen(address):
        fs_unset()
    else:
        fs_set(True)

if (mode == 'm'):
    lib.withFocus(address, fs_max)
elif (mode == 'c'):
    lib.withFocus(address, fs_cycle)
elif (mode == 's'):
    lib.withFocus(address, fs_set)
elif (mode == 'u'):
    lib.withFocus(address, fs_unset)
else:
    lib.exit(f'mode [{mode}] invalid', 1)
