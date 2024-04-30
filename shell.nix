{ pkgs ? import <nixpkgs> {}}:

pkgs.mkShell {
  packages = [ 
    pkgs.rofi
    pkgs.nodejs
    pkgs.yarn
    (pkgs.python3.withPackages (python-pkgs: [
      python-pkgs.mpd2
      python-pkgs.dmenu-python
    ]))
  ];
}
