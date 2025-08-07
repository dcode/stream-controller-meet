#!/bin/sh
# This script ensures we use the correct python and finds the proxy script
# relative to this script's location, making the setup more portable.

DIR=$(dirname "$0")
# Assuming you have a python executable available in the PATH that Chrome can run.
exec python "$DIR/meet_proxy.py"
