let
  # 
  # Note that I am using a snapshot from NixOS unstable here
  # so that we can use a more bleeding edge version which includes the test --ui . 
  # If you want use a different version, go to nix packages search, and find the 
  # github hash of the version you want to be using, then replace in the URL below.
  #
  nixpkgs = builtins.fetchTarball "https://github.com/NixOS/nixpkgs/archive/4059c4f71b3a7339261c0183e365fd8016f24bdb.tar.gz";
  pkgs = import nixpkgs { config = { }; overlays = [ ]; };
in
with pkgs;
mkShell {
  buildInputs = [
    nodejs
    playwright-test
    # python311Packages.playwright
    # python311Packages.pytest
  ];

  PLAYWRIGHT_BROWSERS_PATH="${pkgs.playwright-driver.browsers}";

  shellHook = ''
    # Remove playwright from node_modules, so it will be taken from playwright-test
    rm node_modules/@playwright/ -R
    export PLAYWRIGHT_BROWSERS_PATH=${pkgs.playwright-driver.browsers}
    export PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=true
  '';
}
