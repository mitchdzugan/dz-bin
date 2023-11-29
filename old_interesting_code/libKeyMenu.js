#!/usr/bin/env node

const fs = require('fs');
const yaml = require('yaml');
const exec = require('child_process').exec;

const C = {
  bg: "#1E1E2E",
  fg: "#CDD6F4",
  black: "#45475A",
  red: "#F38BA8",
  green: "#A6E3A1",
  yellow: "#F9E2AF",
  blue: "#89B4FA",
  magenta: "#F5C2E7",
  cyan: "#94E2D5",
  white: "#BAC2DE",
  bright: {
    black: "#585B70",
    get red() { return C.red },
    get green() { return C.green; },
    get yellow() { return C.yellow; },
    yellow: "#fab388",
    blue: "#b4befe",
    magenta: "#cba6f7",
    cyan: "#74c7ec",
    white: "#A6ADC8",
  },
};

const alpha = (color, a) => `${color}${a}`;

const WHICH_KEY = '/home/mitch/Projects/wlr-which-key/target/debug/wlr-which-key';
const baseConfig = {
  font: "Serious Sans Nerd Font Mono 12",
  background: alpha(C.bg, "77"),
  color: C.bright.cyan,
  color_key: C.bright.magenta,
  color_mod: C.bright.blue,
  color_sep: C.bright.black,
  color_and: C.bright.yellow,
  color_cmd: C.yellow,
  border: alpha(C.blue, "77"),

  separator: " : ",
  title_separator: " / ",
  border_width: 1,
  column_spacing: 3,
  corner_radius: 0,
  padding: 35,
  anchor: "center",
};

const run = (config) => {
  const cmd = `echo '${JSON.stringify(config)}' | ${WHICH_KEY}`
  console.log(JSON.stringify(config, null, ' '));
  exec(cmd, (err, stdout_, stderr_) => {
    const stdout = stdout_.toString("utf-8");
    const stderr = stderr_.toString("utf-8");
    if (stderr) {
      console.error(stderr.substr(0, stderr.length-1));
    }
    if (stdout) {
      let found = false;
      if (stdout.startsWith("fn_cmd\t")) {
        const parts = stdout.trim().substr(7).split(",").map(s => parseInt(s));
        const key = parts.slice(0, parts.length-1).join(",");
        const ind = parts[parts.length-1];
        const source = fullmap[key] || [];
        if (ind > 0 && ind < source.length && source[ind].fn) {
          found = true;
          source[ind].fn();
        }
      }
      if (!found) {
        console.log(stdout.substr(0, stdout.length-1));
      }
    }
    process.exit(err);
  });
};

let path = [];
let fullmap = {};

const pathKey = (p = path) => p.join(",");
const currPathInd = () => {
  const key = pathKey();
  const curr = fullmap[key] || [];
  fullmap[key] = curr;
  const ind = curr.length - 1;
  if (ind < 0) {
    console.error(fullmap);
    console.error(path);
    throw "no current path";
  }
  return ind;
}
const currPathData = () => {
  const key = pathKey();
  const curr = fullmap[key] || [];
  return curr[currPathInd()];
}
const currPathKey = () => {
  return [...path, currPathInd()].join(",");
};

const push_child = (type, k, data) => {
  const key = pathKey();
  const curr = fullmap[key] || [];
  fullmap[key] = curr;
  curr.push({ ...data, type, k });
};

const spread_data = (data) => {
  const key = pathKey();
  const curr = fullmap[key] || [];
  const ind = currPathInd();
  curr[ind] = { ...curr[ind], ...data };
};

const _cmd = (res, menu) => (k_, desc, cmd) => {
  const [k, after] = (typeof k_) === 'string' ?
    [k_, () => res] :
    [k_.key, k_.after];
  push_child('cmd', k, { desc, cmd });
  menu.push({ key: k, desc, var: { cmd } });
  return after(res);
};
const _alt_var = (res, menu) => (config_key, config_val) => {
  const curr = menu[menu.length - 1];
  curr.var[config_key] = config_val;
  return res;
};
const _alt = (res, menu) => (config_key, config_val) => {
  const curr = menu[menu.length - 1];
  curr[config_key] = config_val;
  return res;
};
const _fn = (res, menu) => (k, desc, fn) => {
  _cmd(res, menu)(k, desc, "");
  const cmd = `echo -e \"fn_cmd\t${currPathKey()}\"`;
  _alt_var(res, menu)("cmd", cmd);
  spread_data({ cmd, fn, type: 'fn' });
  return res;
}
const _sub = (res, menu) => (k_, ...args) => {
  const [k, after] = (typeof k_) === 'string' ?
    [k_, () => res] :
    [k.key, k.after];
  const [f, title, desc = title] = (() => { const a = [...args]; a.reverse(); return a; })();
  push_child('sub', k, { desc });
  const pathInd = currPathInd();
  const curr_path = path;
  path = [...curr_path, pathInd];
  const newcols = [];
  const submenu = [];
  menu.push({ key: k, desc, var: { rec: { title, newcols, items: submenu } } });
  const _ = {};
  _.sub = _sub(_, submenu);
  _.cmd = _cmd(_, submenu);
  _.alt = _alt(_, submenu);
  _.fn = _fn(_, submenu);
  _.col = () => { newcols.push(currPathInd() + 1); return _; }
  f(_);
  path = curr_path;
  return after(res);
};
const PMenu = (title, f) => {
  path = [];
  fullmap = {};
  const newcols = [];
  const config = { ...baseConfig, menu: { title, newcols, items: [] } };
  const _ = {};
  _.sub = _sub(_, config.menu.items);
  _.cmd = _cmd(_, config.menu.items);
  _.alt = _alt(_, config.menu.items);
  _.fn = _fn(_, config.menu.items);
  _.col = () => { newcols.push(currPathInd() + 1); return _; }
  f(_);
  console.log(JSON.stringify(config));
};
const Menu = (title, f) => {
  path = [];
  fullmap = {};
  const newcols = [];
  const config = { ...baseConfig, menu: { title, newcols, items: [] } };
  const _ = {};
  _.sub = _sub(_, config.menu.items);
  _.cmd = _cmd(_, config.menu.items);
  _.alt = _alt(_, config.menu.items);
  _.fn = _fn(_, config.menu.items);
  _.col = () => { newcols.push(currPathInd() + 1); return _; }
  f(_);
  run(config);
};

const has = (all, mod) => (all & mod) === mod;
const all = (...mods) => mods.reduce((a, b) => a | b, 0)

const MOD = { CTL: 1, ALT: 2, SHIFT: 4, SUPER: 8 };
const MOD_SYM = {
  [MOD.CTL]:   "⌃",
  [MOD.ALT]:   "⎇",
  [MOD.SHIFT]: "⇧",
  [MOD.SUPER]: "❖",
}

const NUM_SHIFT = {
  0: ")",
  1: "!",
  2: "@",
  3: "#",
  4: "$",
  5: "%",
  6: "^",
  7: "&",
  8: "*",
  9: "(",
};

const NumKey = (n) => (mod) => ({
  key: has(mod, MOD.SHIFT) ? NUM_SHIFT[n] : `${n}`,
  after: (_ => _.alt("display_key", `${n}`))
})

const Key = {
  tab: (mod) => ({
    key: has(mod, MOD.SHIFT) ? "ISO_Left_Tab" : "Tab",
    after: (_ => _.alt("display_key", "[tab]"))
  }),
  0: NumKey(0),
  1: NumKey(1),
  2: NumKey(2),
  3: NumKey(3),
  4: NumKey(4),
  5: NumKey(5),
  6: NumKey(6),
  7: NumKey(7),
  8: NumKey(8),
  9: NumKey(9),
};

module.exports.Menu = Menu;
module.exports.PMenu = PMenu;
module.exports.MOD = MOD;
module.exports.Key = {};
Object.keys(Key).forEach((k) => {
  module.exports.Key[k] = (...mods) => {
    const res = Key[k](all(...mods));
    const display_mod = mods.map(m => MOD_SYM[m] || "").join("");
    return {
      key: res.key,
      after: (_) => {
        if (display_mod) {
          _.alt("display_mod", display_mod)
        }
        return res.after(_);
      },
    };
  };
});
