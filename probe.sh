#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
DEVS=$(cat ./devs)

echo "# Coupler list"
for d in $DEVS; do
	if ! ping -W 1 -c 1 $d > /dev/null; then
		echo -e "## Skipping $d, not online\n"
	else
		echo -e "## $d"
		./ekctl.py --version --ip=$d
		echo -e "\n"
	fi
done

