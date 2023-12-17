#!/usr/bin/python3

import os
import lib

spec = lib.ArgsSpec()
spec._(lib.add_address_arg)
spec.curr.help = """
wayland client address to lower. default focused
"""
args = spec.parse_args()

address = args.address
client = lib.getClient(address)
address = client["address"]
floating = client["floating"]
fullscreen = client["fullscreen"]
fakeFullscreen = client["fakeFullscreen"]
fullscreenMode = client["fullscreenMode"]

if fakeFullscreen and floating:
    if (lib.isMaxFakeFullscreen(address)):
        lib.restoreMaximizedFakeFullscreen(address)
    else:
        lib.hyprctl("togglefloating")
elif fullscreen:
    if fullscreenMode == 0:
        os.system('hyprctl --batch "dispatch fullscreen ; dispatch fullscreen 1"')
    else:
        lib.hyprctl("fullscreen")
elif floating:
    lib.hyprctl("togglefloating")
else:
    print("lowest")
