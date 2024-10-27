{ pkgs ? import <nixpkgs> {}}:

pkgs.mkShell {
  packages = [ 
    pkgs.rofi-wayland
    pkgs.nodejs
    pkgs.yarn
    (pkgs.python3.withPackages (python-pkgs: [
      python-pkgs.beautifulsoup4
      python-pkgs.dmenu-python
      python-pkgs.mpd2
      python-pkgs.requests
    ]))
  ];
}
