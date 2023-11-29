#!/usr/bin/python3

import dmenu
import json
import os
import subprocess
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))

refs = {}
labels = []

def addSubfolders(name, path):
    for sub in os.listdir(path):
        label = f"{name} | {sub}"
        fullPath = f"{path}/{sub}"
        refs[label] = fullPath
        labels.append(label)

addSubfolders("projects", "/home/mitch/Projects")
addSubfolders("configs", "/home/mitch/.config")

ff_css_path = "/home/mitch/.mozilla/firefox/4hhe50hl.default-release/chrome"
dz_bin_path = "/home/mitch/.local/bin"
ff_css_label = f"firefox | user-chrome"
dz_bin_label = f"󰯁scripts | dz-bin"
labels.append(ff_css_label)
labels.append(dz_bin_label)
refs[ff_css_label] = ff_css_path
refs[dz_bin_label] = dz_bin_path

selectedLabel = dmenu.show(
    labels,
    command=f"{dir_path}/rofi-dmenu",
    prompt='Open Project',
    case_insensitive=True
)

if selectedLabel in refs:
    path = refs[selectedLabel]
    # os.system(f'cd {path} && neovide ./')
    os.system(f'pushd {path} && nvim ./ && popd')
