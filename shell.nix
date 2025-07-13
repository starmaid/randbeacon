let
  pkgs = import <nixpkgs> {};
in pkgs.mkShell {
  packages = with pkgs; [
    (pkgs.python3.withPackages (python-pkgs: [
      python-pkgs.requests
    ]))
    chromium
  ];
}