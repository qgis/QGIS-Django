#!/usr/bin/env bash

source playwright-path.sh

echo "This script will run the tests defined in tests/"
echo "Before running the tests you need to create the auth config"
echo ""

$PLAYWRIGHT \
    test \
    --ui \
    --project chromium

echo "--done--"
