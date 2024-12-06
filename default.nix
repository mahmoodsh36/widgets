{ pkgs ? import <nixpkgs> {} }:
let
    src = /home/mahmooz/work/widgets/menu.py;
in
with pkgs;
python3.pkgs.buildPythonApplication {
  pname = "widgets";
  src = src;
  buildInputs = [
    gtk3
    gtk4
    glib
    wrapGAppsHook
    gobject-introspection
    cairo
  ];
  nativeBuildInputs = [
    intltool
    file
    gtk3
    gtk4
    glib
    gobject-introspection
    wrapGAppsHook
  ];
  propagatedBuildInputs = with python3Packages; [
    distutils_extra
    setuptools
    pygobject3
    pygobject4
    pillow
    dbus-python
    pycairo
    distutils_extra
    setuptools
  ];
  python = python3;
  dbus_python = python3Packages.dbus-python;
  meta = {
    maintainers = with maintainers; [ trizen ];
  };
  dontUnpack = true;
  dontBuild = true;

  installPhase = ''
    mkdir -p $out/bin
    cp ${src} $out/bin/menu.py
    chmod +x $out/bin/menu.py
  '';

  format = "other";
}