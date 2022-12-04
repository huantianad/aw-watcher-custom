{
  description = "My custom process watcher (for use with ActivityWatch).";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";

    flake-utils.url = "github:numtide/flake-utils";

    jtojnar.url = "github:jtojnar/nixfiles";
    jtojnar.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, flake-utils, jtojnar }:
    flake-utils.lib.eachDefaultSystem (system:
    let
      pkgs = nixpkgs.legacyPackages.${system};
      python3 = pkgs.python310;
      aw-client = jtojnar.legacyPackages.${system}.aw-client;
    in {
      devShells.default = pkgs.mkShell {
        nativeBuildInputs = with pkgs; with python3.pkgs; [
          black
          poetry-core
          setuptools
          aw-client
          psutil
        ];
      };

      packages.default = python3.pkgs.buildPythonApplication {
        pname = "aw-watcher-custom";
        version = "0.1.0";

        format = "pyproject";

        src = ./.;

        nativeBuildInputs = with python3.pkgs; [
          poetry-core
        ];

        propagatedBuildInputs = with python3.pkgs; [
          setuptools
          aw-client
          psutil
        ];

        meta = with pkgs.lib; {
          description = "My custom process watcher (for use with ActivityWatch).";
          homepage = "https://github.com/huantianh/aw-watcher-custom";
          maintainers = with maintainers; [ huantian ];
          license = licenses.mit;
        };
      };
    });
}
