{
  description = "PDF manipulation tools";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        python = pkgs.python3;
        pythonEnv = python.withPackages (ps: with ps; [
          pypdf2
          rich  # For nice CLI output
          typer # For CLI interface
        ]);
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            pythonEnv
            pkgs.black    # Python formatter
            pkgs.ruff     # Fast Python linter
          ];

          shellHook = ''
            export PYTHONPATH="$PWD:$PYTHONPATH"
            echo "PDF Tools Development Environment"
            echo "Available Python packages: PyPDF2, Rich, Typer"
          '';
        };
      });
}
