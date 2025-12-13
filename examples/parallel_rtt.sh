#!/bin/bash

# Usage: ./parallel_rtt.sh [--mcu MCU_NAME] [--timeout SECONDS] ip1 ip2 ip3 ...
#    or: ./parallel_rtt.sh [--mcu MCU_NAME] [--timeout SECONDS] $(cat ips.txt)

if [ $# -lt 1 ]; then
    echo "Usage: $0 [--mcu MCU_NAME] [--timeout SECONDS] <ip1> [ip2] ..."
    echo ""
    echo "Options:"
    echo "  --mcu MCU_NAME      Specify MCU type (e.g., STM32F765ZG)"
    echo "                      If not specified, auto-detection will be used"
    echo "  --timeout SECONDS   RTT read timeout in seconds (default: 10)"
    echo "                      Use 0 for infinite (Ctrl+C to stop)"
    echo ""
    echo "Examples:"
    echo "  $0 192.168.1.100 192.168.1.101"
    echo "  $0 --mcu STM32F765ZG --timeout 30 192.168.1.100"
    echo "  $0 --timeout 0 \$(cat ips.txt)"
    echo ""
    echo "Output files will be saved as: rtt_<ip>.log"
    exit 1
fi

MCU=""
TIMEOUT="10"

while [[ $# -gt 0 ]]; do
    case $1 in
        --mcu)
            MCU="$2"
            shift 2
            ;;
        --timeout|-t)
            TIMEOUT="$2"
            shift 2
            ;;
        *)
            break
            ;;
    esac
done

IPS=("$@")

if [ ${#IPS[@]} -eq 0 ]; then
    echo "Error: No IP addresses provided"
    exit 1
fi

# Create output directory with timestamp
OUTPUT_DIR="rtt_logs_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"
echo "Output directory: $OUTPUT_DIR"
echo ""

STOPPING=0

cleanup() {
    if [ $STOPPING -eq 0 ]; then
        STOPPING=1
        echo ""
        echo "Stopping all RTT readers..."
        kill 0 2>/dev/null
    fi
}

trap cleanup INT TERM

read_rtt() {
    local ip="$1"
    local mcu="$2"
    local timeout="$3"
    local logfile="$OUTPUT_DIR/rtt_${ip}.log"
    
    local cmd="bmlab-jlink-rtt --ip $ip -t $timeout"
    [ -n "$mcu" ] && cmd="$cmd --mcu $mcu"
    
    # Remove ANSI color codes and write unbuffered
    $cmd 2>&1 | stdbuf -oL sed 's/\x1b\[[0-9;]*m//g' > "$logfile"
    local exit_code=${PIPESTATUS[0]}
    
    if [ $exit_code -eq 0 ]; then
        echo "$ip OK (saved to $logfile)"
    else
        echo "$ip FAULT (see $logfile)"
    fi
}

echo "Starting RTT readers for ${#IPS[@]} device(s)..."
echo "Timeout: ${TIMEOUT}s (0 = infinite)"
echo ""

for ip in "${IPS[@]}"; do
    read_rtt "$ip" "$MCU" "$TIMEOUT" &
done

wait

echo ""
echo "All RTT sessions completed"
