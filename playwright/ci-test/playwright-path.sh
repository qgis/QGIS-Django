#!/usr/bin/env bash

echo "This script will discover the path to your playwright install"
echo "If you are not in a NixOS environment and it is not installed,"
echo "playwright will be installed."
echo ""
echo "At the end of calling this script , you should have a PLAYWRIGHT"
echo ""

# Are we on nixos or a distro with Nix installed for packages
# Y
  # Are we in direnv?
  # Y: should all be set up
  # N: run nix-shell
#N
 # Are we in a deb based distro?
 # Are we in an rpm based distro?
 # Are we on macOS?
 # Are we in windows?

HAS_PLAYWRIGHT=$(which playwright 2> /dev/null | grep -v "which: no" | wc -l)
PLAYWRIGHT="playwright"
if [ $HAS_PLAYWRIGHT -eq 0 ]; then
	PLAYWRIGHT="npx playwright"
  
    	# check if OS is a deb based distro and uses apt
    	USES_APT=$(which apt 2> /dev/null | grep -w "apt" | wc -l)
		# check if OS is an rpm-based distro
  		USES_RPM=$(which rpm | grep -w "rpm" | wc -l)
    
    	if [ $USES_APT -eq 1 ]; then
			# check if nodejs is installed
			HAS_NODEJS=$(which node | grep -w "node" | wc -l)

			# if nodejs is present then
    		if [ $HAS_NODEJS -eq 0 ]; then
			source nodesource-install.sh
    		fi

    		# check if npm is present
    		HAS_NPM=$(which npm | grep -w "npm" | wc -l)

    		if [ $HAS_NPM -eq 1 ]; then
				NPM="npm"
				PLAYWRIGHT_INSTALL=$($NPM ls --depth 1 playwright | grep -w "@playwright/test" | wc -l)

				if [ $PLAYWRIGHT_INSTALL -eq 0 ]; then
					$NPM install -D @playwright/test@latest
					$NPM ci
					$PLAYWRIGHT install --with-deps chromium
				fi

    		fi

  		elif [ $USES_RPM -eq 1 ]; then

    			# check if nodejs is installed
    			HAS_NODEJS=$(which node | grep -w "node" | wc -l)

    			# if nodejs is present then
    			if [ $HAS_NODEJS -eq 0 ]; then
      				source nodesource-install.sh
    			fi

    			# check if npm is present
    			HAS_NPM=$(which npm | grep -w "npm" | wc -l)

    			if [ $HAS_NPM -eq 1 ]; then
      				NPM="npm"
					PLAYWRIGHT_INSTALL=$($NPM ls --depth 1 playwright | grep -w "@playwright/test" | wc -l)

      				if [ $PLAYWRIGHT_INSTALL -eq 0 ]; then
        				$NPM install -D @playwright/test@latest
        				$NPM ci
        				$PLAYWRIGHT install
      				fi

    			fi
		fi
fi

echo "Done."
echo ""
