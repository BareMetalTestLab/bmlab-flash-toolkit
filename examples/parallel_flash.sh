#!/bin/bash

# Usage: ./parallel_flash.sh [--mcu MCU_NAME] firmware.bin ip1 ip2 ip3 ...
#    or: ./parallel_flash.sh [--mcu MCU_NAME] firmware.bin $(cat ips.txt)

if [ $# -lt 2 ]; then
    echo "Usage: $0 [--mcu MCU_NAME] <firmware.bin> <ip1> [ip2] ..."
    echo ""
    echo "Options:"
    echo "  --mcu MCU_NAME    Specify MCU type (e.g., STM32F765ZG)"
    echo "                    If not specified, auto-detection will be used"
    echo ""
    echo "Examples:"
    echo "  $0 firmware.bin 192.168.1.100 192.168.1.101"
    echo "  $0 --mcu STM32F765ZG firmware.bin 192.168.1.100"
    echo "  $0 firmware.bin \$(cat ips.txt)"
    exit 1
fi

MCU=""
if [ "$1" = "--mcu" ]; then
    MCU="$2"
    shift 2
fi

FIRMWARE="$1"
shift
IPS=("$@")

flash_device() {
    if [ -n "$2" ]; then
        bmlab-flash --ip "$1" --mcu "$2" "$3" >/dev/null 2>&1
    else
        bmlab-flash --ip "$1" "$3" >/dev/null 2>&1
    fi
    
    if [ $? -eq 0 ]; then
        echo "$1 OK"
    else
        echo "$1 FAULT"
    fi
}

for ip in "${IPS[@]}"; do
    flash_device "$ip" "$MCU" "$FIRMWARE" &
done

wait
