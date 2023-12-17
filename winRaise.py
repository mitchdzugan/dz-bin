#!/usr/bin/python3

import os
import lib

spec = lib.ArgsSpec()
spec._(lib.add_address_arg)
spec.curr.help = """
wayland client address to raise. default focused
"""
args = spec.parse_args()

address = args.address
client = lib.getClient(address)
address = client["address"]
floating = client["floating"]
fullscreen = client["fullscreen"]
fakeFullscreen = client["fakeFullscreen"]
fullscreenMode = client["fullscreenMode"]

lib.focus(address)
if not floating:
    os.system(f"hyprctl dispatch togglefloating")
    client = lib.getClient(address, True)
    size = lib.boundSize(client["size"])
    at = lib.center(size)
    [w, h] = size
    [l, t] = at
    target = f'address:{address}'
    lib.hyprctl(f'resizewindowpixel exact {w} {h},{target}')
    lib.hyprctl(f'movewindowpixel exact {l} {t},{target}')
elif fakeFullscreen:
    if not lib.isMaxFakeFullscreen(address):
        lib.setFloatData(address)
    lib.maximizeFakeFullscreen(address)
elif not fullscreen:
    os.system(f"hyprctl dispatch fullscreen 1")
else:
    os.system('hyprctl --batch "dispatch fullscreen ; dispatch fullscreen 0"')
