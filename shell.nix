{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  nativeBuildInputs = with pkgs; [
    gobject-introspection
  ];
  buildInputs = with pkgs; [
    gtk3
    gtk-layer-shell
    # gtk4-layer-shell
    # gtk4
    gobject-introspection
    (python3.withPackages (p: with p; [
      pygobject3
      pydbus
    ]))
  ];
}
