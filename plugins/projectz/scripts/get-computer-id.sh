#!/bin/bash
# get-computer-id.sh - Get computer's unique ID (MAC address)
# Works on macOS and Linux

set -e

get_mac_macos() {
    # Try en0 first (WiFi), then en1 (Ethernet)
    for iface in en0 en1 en2; do
        mac=$(ifconfig "$iface" 2>/dev/null | grep ether | awk '{print $2}' | tr -d ':' | tr '[:upper:]' '[:lower:]')
        if [ -n "$mac" ]; then
            echo "$mac"
            return 0
        fi
    done
    return 1
}

get_mac_linux() {
    # Try common interface names
    for iface in eth0 enp0s3 ens33 wlan0 wlp2s0; do
        if [ -f "/sys/class/net/$iface/address" ]; then
            mac=$(cat "/sys/class/net/$iface/address" | tr -d ':' | tr '[:upper:]' '[:lower:]')
            if [ -n "$mac" ] && [ "$mac" != "000000000000" ]; then
                echo "$mac"
                return 0
            fi
        fi
    done

    # Fallback: first non-loopback interface
    for addr_file in /sys/class/net/*/address; do
        iface=$(dirname "$addr_file" | xargs basename)
        if [ "$iface" != "lo" ]; then
            mac=$(cat "$addr_file" | tr -d ':' | tr '[:upper:]' '[:lower:]')
            if [ -n "$mac" ] && [ "$mac" != "000000000000" ]; then
                echo "$mac"
                return 0
            fi
        fi
    done
    return 1
}

# Detect OS and get MAC
case "$(uname -s)" in
    Darwin)
        get_mac_macos
        ;;
    Linux)
        get_mac_linux
        ;;
    *)
        echo "Unsupported OS: $(uname -s)" >&2
        exit 1
        ;;
esac
