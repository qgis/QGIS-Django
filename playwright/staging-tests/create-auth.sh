#!/usr/bin/env bash

source base-url.sh

source playwright-path.sh

echo "This script will write a new test to tests/deleteme.spec.ts"
echo "then delete it, leaving only the auth config."
echo ""
echo "When the playwright browser opens, log in to the site then exit."
echo "After recording your test, close the test browser."
echo "Recording auth token to auth.json"

# File exists and write permission granted to user
# show prompt
echo "Continue? y/n"
read ANSWER
case $ANSWER in 
  [yY] ) echo "Writing auth.json" ;;
  [nN] ) echo "Cancelled."; exit ;;
esac

$PLAYWRIGHT \
	codegen \
	--target playwright-test \
	--save-storage=auth.json \
	-o tests/deleteme.spec.ts \
	$BASE_URL

# We are only interested in auth.json
rm tests/deleteme.spec.ts

echo "Auth file creation completed."
echo "You can then run your tests by doing e.g.:"
echo "playwright test --project chromium"
