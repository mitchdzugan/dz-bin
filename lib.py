from argparse import ArgumentParser
import dmenu
import json
import os
import subprocess
import sys
import time

class ArgSpec:
    def __init__(self, argsSpec, pos):
        self.argsSpec = argsSpec
        self.pos = pos

    def setProp(self, k, v):
        self.argsSpec.args[self.pos]["p"][k] = v

    @property
    def default(self): return None
    @default.setter
    def default(self, v): self.setProp("default", v)

    @property
    def help(self): return None
    @help.setter
    def help(self, v): self.setProp("help", v)

    @property
    def abbrev(self): return None
    @abbrev.setter
    def abbrev(self, v): self.argsSpec.args[self.pos]["abbrev"] = v

    @property
    def post(self): return None
    @post.setter
    def post(self, f): self.argsSpec.args[self.pos]["post"] = f

class ArgsSpec:
    def __init__(self):
        self.args = {}
        self.idByName = {}
        self.nextId = 0
        self.lastId = None
        self.props = {}

    def _(self, f):
        f(self)

    def parse_args(self):
        parser = ArgumentParser(**self.props)
        if "pos" in self.args:
            pos = self.args["pos"]
            parser.add_argument(pos["name"], **pos["p"])
        for i in range(self.nextId):
            arg = self.args[i]
            name = f"--{arg['name']}"
            abbrev = None
            if "abbrev" in arg:
                abbrev = f"-{arg['abbrev']}"
            if abbrev != None:
                parser.add_argument(abbrev, name, **arg["p"])
            else:
                parser.add_argument(name, **arg["p"])
        parsed = parser.parse_args()
        if "pos" in parsed and "post" in self.args["pos"]:
            parsed.pos = self.args["pos"]["post"](parsed.pos)
        for i in range(self.nextId):
            arg = self.args[i]
            name = arg['name']
            if name in parsed and "post" in arg:
                setattr(parsed, name, arg["post"](getattr(parsed, name)))
        return parsed

    @property
    def curr(self):
        return ArgSpec(self, self.lastId)
    @curr.setter
    def curr(self, k):
        if (k == "pos") or (not isinstance(k, str)):
            self.lastId = k
        else:
            self.lastId = self.idByName[k]

    def addArg(self, name, id=None, **initProps):
        if (id == None):
            id = self.nextId
            self.nextId += 1
        self.lastId = id
        self.args[id] = {"name": name, "p": initProps}
        self.idByName[name] = id

    @property
    def arg(self): return None
    @arg.setter
    def arg(self, name): self.addArg(name)

    @property
    def flg(self): return None
    @flg.setter
    def flg(self, name): self.addArg(name, action='store_true')

    @property
    def pos(self): return ArgSpec(self, "pos")
    @pos.setter
    def pos(self, name): self.addArg(name, id="pos")

    @property
    def desc(self): return None
    @desc.setter
    def desc(self, desc): self.props["description"] = desc

def add_address_arg(spec):
    spec.arg = 'address'
    spec.curr.post = lambda a: a if a != None else focused()
    spec.curr.abbrev = 'a'
    spec.curr.help = """
wayland client address. default focused
"""

ROUNDING = 10
SW = 1920
SH = 1080
MARGIN = 20
BAR_HEIGHT = 26

def boundSize(size):
    w = min(size[0], SW - MARGIN)
    h = min(size[1], SH - MARGIN - BAR_HEIGHT)
    return [w, h]

def center(size):
    [w, h] = size
    l = int(((SW - 0         ) / 2) - (w / 2))
    t = int(((SH - BAR_HEIGHT) / 2) - (h / 2))
    return [l, t]

bindir = os.path.dirname(os.path.realpath(__file__))
statedir = f"{bindir}/state/"
pendingdir = f"{statedir}/pending/"
floatdir = f"{statedir}/floating/"
tmpdir = f"{statedir}/temp/"

def exists(filename):
    print()
    print(filename)
    print(os.path.isfile(filename))
    return os.path.isfile(filename)

def existsBin(basename):
    return exists(f"{bindir}/{basename}")

def existsState(basename):
    return exists(f"{statedir}/{basename}")

def existsPending(basename):
    return exists(f"{pendingdir}/{basename}")

def existsFloat(basename):
    return exists(f"{floatdir}/{basename}")

def existsTmp(basename):
    return exists(f"{tmpdir}/{basename}")

def slurp(filename):
    if (not exists(filename)):
        return None
    data = ""
    with open(filename) as f:
        data = f.read()
    return data

def slurpBin(basename):
    return slurp(f"{bindir}/{basename}")

def slurpState(basename):
    return slurp(f"{statedir}/{basename}")

def slurpPending(basename):
    return slurp(f"{pendingdir}/{basename}")

def slurpFloat(basename):
    return slurp(f"{floatdir}/{basename}")

def slurpTmp(basename):
    return slurp(f"{tmpdir}/{basename}")

def spit(filename, s, dashP = False):
    if dashP:
        os.system(f'mkdir -p {os.path.dirname(filename)}')
    with open(filename, "w") as f:
        data = f.write(s)

def spitBin(basename, s, dashP = False):
    return spit(f"{bindir}/{basename}", s, dashP)

def spitState(basename, s, dashP = False):
    return spit(f"{statedir}/{basename}", s, dashP)

def spitPending(basename, s, dashP = False):
    return spit(f"{pendingdir}/{basename}", s, dashP)

def spitFloat(basename, s, dashP = False):
    return spit(f"{floatdir}/{basename}", s, dashP)

def spitTmp(basename, s, dashP = False):
    return spit(f"{tmpdir}/{basename}", s, dashP)

def cmdsPipe(*cmds):
    last = None
    for cmd in cmds:
        if last == None:
            last = subprocess.run(
                cmd, stdout=subprocess.PIPE
            )
        else:
            last = subprocess.run(
                cmd, input=last.stdout, stdout=subprocess.PIPE
            )
    return last.stdout.decode()

def cmdText(cmd):
    argv = cmd.split(" ")
    result = subprocess.run(argv, stdout=subprocess.PIPE)
    return result.stdout.decode().strip()

def cmdJson(cmd):
    return json.loads(cmdText(cmd))

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
    print(client)
    return {
        "address": address,
        "pid": pid,
        "floating": floating,
        "fullscreen": client["fullscreen"],
        "fullscreenMode": client["fullscreenMode"],
        "fakeFullscreen": client["fakeFullscreen"],
        "workspace": workspace,
        "workspaceId": workspaceId,
        "class": cclass,
        "title": title,
        "at": client["at"],
        "size": client["size"]
    }

clientsCache = None
def getClients(skipCache=False):
    global clientsCache
    if (clientsCache != None and not skipCache):
        return clientsCache
    clientsCache = list(map(getClientData, cmdJson('hyprctl clients -j')))
    return clientsCache

clientsByACache = None
def getClientsByAddress(skipCache=False):
    global clientsByACache
    if (clientsByACache != None and not skipCache):
        return clientsByACache
    clients = getClients(skipCache)
    clientsByACache = {}
    for client in clients:
        clientsByACache[client["address"]] = client
    return clientsByACache

def getClient(address, skipCache=False):
    return getClientsByAddress(skipCache)[address]

activeWindowCache = None
def getActiveWindow(skipCache=False):
    global activeWindowCache
    if (activeWindowCache != None and not skipCache):
        return activeWindowCache
    activeWindowCache = cmdJson('hyprctl activewindow -j')
    return activeWindowCache

def focused(skipCache=False):
    return getActiveWindow(skipCache)["address"]

def hyprctl(cmd):
    os.system(f'hyprctl dispatch {cmd}')

def setprop(address, prop, val, lock=False):
    locks = "lock" if lock else ""
    print(f'hyprctl setprop address:{address} {prop} {val} {locks}')
    os.system(f'hyprctl setprop address:{address} {prop} {val} {locks}')

def exit(a1=None, a2=None):
    msg = None
    code = None
    if (a1 != None):
        if (isinstance(a1, str)):
            msg = a1
            code = a2
        else:
            msg = a2
            code = a1
    if (msg != None):
        print(msg, file=sys.stderr)
    if (code != None):
        sys.exit(code)
    else:
        sys.exit()

def setFloatData(address):
    client = getClient(address)
    if (client["workspaceId"] == -99) or (not client["floating"]):
        return
    floatData = { "was": True }
    floatData["at"] = client["at"]
    floatData["size"] = client["size"]
    spitFloat(address, json.dumps(floatData))

def setRawFloatData(address, d_at, d_size):
    floatData = { "was": True }
    floatData["at"] = d_at
    floatData["size"] = d_size
    spitFloat(address, json.dumps(floatData))

def getFloatData(address):
    floatData = json.loads(slurpFloat(address) or "{\"was\":false}")
    if floatData["was"]:
        floatData["sizestr"] = f'{floatData["size"][0]} {floatData["size"][1]}'
        floatData["movestr"] = f'{floatData["at"][0]} {floatData["at"][1]}'
    return floatData

def focus(address):
    hyprctl(f'focuswindow address:{address}')

def withFocus(address, fn):
    prevFocus = cmdJson('hyprctl activewindow -j')["address"]
    focus(address)
    fn()
    focus(prevFocus)

def moveWindow(address, workspace):
    window = f'address:{address}'
    activeWorkspace = cmdJson('hyprctl activeworkspace -j')
    activeWorkspaceId = int(activeWorkspace["id"])
    dir = "up"
    wasTemp = address == (slurpTmp("address") or "").strip()
    if (workspace != "special"):
        targetWorkspaceId = int(workspace)
        if targetWorkspaceId == activeWorkspaceId:
            dir = "no"
        elif targetWorkspaceId > activeWorkspaceId:
            dir = "right"
        else:
            dir = "left"
    curr = getClient(address)
    if curr['workspace'] == f"{workspace}":
        dir = 'no'
    print(dir)
    if (dir != "no"):
        if not curr["floating"]:
            hyprctl(f"togglefloating {window}")
            hyprctl(f'resizewindowpixel exact 1000 384,{window}')
            hyprctl(f'movewindowpixel exact 460 12,{window}')
            time.sleep(0.5)
        elif not wasTemp:
            setFloatData(address)
        # animate l/r/u/d
        hyprctl(f'resizewindowpixel exact 1 1,{window}')
        if (dir == 'left'):
            hyprctl(f'movewindowpixel exact 0 540,{window}')
        elif (dir == 'right'):
            hyprctl(f'movewindowpixel exact 1920 540,{window}')
        else:
            hyprctl(f'movewindowpixel exact 960 0,{window}')
        time.sleep(0.5)
    if (f"{workspace}" == activeWorkspace["name"]):
        hyprctl(f'movetoworkspacesilent {workspace},{window}')
    else:
        hyprctl(f'movetoworkspacesilent special,{window}')
    if (f"{workspace}" == activeWorkspace["name"]):
        floatData = getFloatData(address)
        os.system(f"rm {floatdir}/{address}")
        if floatData["was"]:
            if not curr["floating"]:
                hyprctl(f"togglefloating {window}")
            sizestr = floatData["sizestr"]
            movestr = floatData["movestr"]
            hyprctl(f'resizewindowpixel exact {sizestr},{window}')
            hyprctl(f'movewindowpixel exact {movestr},{window}')
        elif curr["floating"]:
            hyprctl(f"togglefloating {window}")
    elif (workspace != 'special'):
        spitPending(f'{workspace}/{address}', '', True)

def maximizeFakeFullscreen(address):
    window = f'address:{address}'
    hyprctl(f'resizewindowpixel exact {SW} {SH},{window}')
    hyprctl(f'movewindowpixel exact {0} {0},{window}')
    setprop(address, 'forcenoborder', 1, True)
    setprop(address, 'rounding', 0, True)

def restoreMaximizedFakeFullscreen(address):
    window = f'address:{address}'
    floatData = getFloatData(address)
    os.system(f"rm {floatdir}/{address}")
    setprop(address, 'forcenoborder', 0, True)
    setprop(address, 'rounding', ROUNDING, True)
    if (floatData["was"]):
        sizestr = floatData["sizestr"]
        movestr = floatData["movestr"]
        hyprctl(f'resizewindowpixel exact {sizestr},{window}')
        hyprctl(f'movewindowpixel exact {movestr},{window}')
    else:
        hyprctl("togglefloating")

def isMaxFakeFullscreen(address):
    client = getClient(address)
    if not client["fakeFullscreen"]: return False
    if client["at"][0] != 0: return False
    if client["at"][1] != 0: return False
    if client["size"][0] != SW: return False
    if client["size"][1] != SH: return False
    return True
