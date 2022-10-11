{
  description = "My custom window watcher (for use with ActivityWatch).";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    jtojnar.url = "github:huantianad/jtojnar-nixfiles";
    jtojnar.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, flake-utils, jtojnar, ... } @ inputs:
    flake-utils.lib.eachDefaultSystem (system:
    let
      pkgs = nixpkgs.legacyPackages.${system};
      python3 = pkgs.python310;
      aw-client = jtojnar.packages.${system}.aw-client;
    in
    {
      defaultPackage = python3.pkgs.buildPythonApplication rec {
        pname = "aw-watcher-custom";
        version = "0.1.0";

        format = "pyproject";

        src = ./.;

        nativeBuildInputs = [
          python3.pkgs.poetry
        ];

        propagatedBuildInputs = with python3.pkgs; [
          setuptools
          aw-client
          psutil
        ];

        meta = with pkgs.lib; {
          description = "My custom window watcher (for use with ActivityWatch).";
          homepage = "https://github.com/huantianh/aw-watcher-custom";
          maintainers = with maintainers; [ huantian ];
          license = licenses.mit;
        };
      };
    });
}
