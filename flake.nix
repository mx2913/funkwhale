{
  description = "Build tauri desktop application";

  inputs = {
    nixpkgs.url = github:NixOS/nixpkgs/nixos-unstable;
    flake-utils = {
      url = "github:numtide/flake-utils";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    rust-overlay.url = "github:oxalica/rust-overlay";
  };

  outputs = inputs: with inputs; flake-utils.lib.eachDefaultSystem (system: let
    pkgs = import nixpkgs {
      inherit system;
      overlays = [
        rust-overlay.overlays.default
      ];
    };
    lib = nixpkgs.lib;

    commonLibraries = with pkgs;[
      # Tauri dependencies
      webkitgtk_4_1
      gtk3
      cairo
      gdk-pixbuf
      glib
      dbus
      openssl_3
      librsvg
      libclang
      libappindicator

      # GStreamer required for audio playback JS-side
      gst_all_1.gstreamer
      gst_all_1.gst-vaapi
      gst_all_1.gst-plugins-bad
      gst_all_1.gst-plugins-ugly
      gst_all_1.gst-plugins-good
      gst_all_1.gst-plugins-base
    ];


    packages = with pkgs; [
      # More tauri dependencies
      curl
      wget
      pkg-config
      libsoup_3
      clang
      rustup

      # Frontend dependencies
      nodejs
      corepack

      # API dependencies / Frontend scripts
      python3
      pre-commit
    ];

  in {
    devShell = pkgs.mkShell {
      buildInputs = commonLibraries ++ packages;

      shellHook = ''
        pre-commit install
      '';

      LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath commonLibraries;

      XDG_DATA_DIRS = let
        base = pkgs.lib.concatMapStringsSep ":" (x: "${x}/share") [
          pkgs.gnome.adwaita-icon-theme
          pkgs.shared-mime-info
        ];

        gsettings-schema = pkgs.lib.concatMapStringsSep ":" (x: "${x}/share/gsettings-schemas/${x.name}") [
          pkgs.glib
          pkgs.gsettings-desktop-schemas
          pkgs.gtk3
        ];

      in "${base}:${gsettings-schema}:$XDG_DATA_DIRS";

      GIO_MODULE_DIR = "${pkgs.glib-networking}/lib/gio/modules/";


      # Avoid white screen running with Nix
      # https://github.com/tauri-apps/tauri/issues/4315#issuecomment-1207755694
      WEBKIT_DISABLE_COMPOSITING_MODE = 1;
    };
  });
}
