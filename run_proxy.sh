#!/bin/sh
# This script ensures we use the correct python and finds the proxy script
# relative to this script's location, making the setup more portable.

DIR=$(dirname "$0")
exec "$DIR/meet_proxy.go"
