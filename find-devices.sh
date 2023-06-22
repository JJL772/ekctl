#!/usr/bin/env bash

set -e
netconfig search "*ek9000*" | grep -E "^\S+:" | sed 's/://g'

