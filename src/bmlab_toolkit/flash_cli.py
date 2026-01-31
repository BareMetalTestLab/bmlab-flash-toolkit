import sys
import os
import time
import argparse
import logging
from concurrent.futures import ProcessPoolExecutor, as_completed

from .constants import SUPPORTED_PROGRAMMERS, DEFAULT_PROGRAMMER, PROGRAMMER_JLINK
from .programmer import Programmer
from .jlink_programmer import JLinkProgrammer


def main(args: argparse.Namespace):
    
    # Validate that --serial and --ip are mutually exclusive
    if args.serial and args.ip:
        print("Error: Cannot specify both --serial and --ip")
        sys.exit(1)

    # Check firmware file exists
    fw_file = os.path.abspath(args.firmware_file)
    if not os.path.exists(fw_file):
        print(f"Error: Firmware file not found: {fw_file}")
        print(f"To list connected devices, run: bmlab-scan")
        sys.exit(1)

    try:
        # Convert log level string to logging constant
        log_level = getattr(logging, args.log_level.upper())

        # Handle IP addresses and serials (convert to list for uniform processing)
        ip_list = args.ip if args.ip else None
        serial_list = args.serial if args.serial else None

        flash_devices(serial_list, ip_list, fw_file, args.mcu, args.programmer, log_level)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def flash_device_task(serial, ip_addr, fw_file, mcu, programmer_type, log_level):
    """Flash a single device (used in parallel execution)."""
    try:
        if programmer_type.lower() == PROGRAMMER_JLINK:
            prog = JLinkProgrammer(serial=serial, ip_addr=ip_addr, log_level=log_level)
        else:
            device_id = ip_addr or serial
            return {'device': device_id, 'success': False, 'error': f"Programmer '{programmer_type}' not implemented"}
        
        if not prog.flash(fw_file, mcu=mcu):
            device_id = ip_addr or serial
            return {'device': device_id, 'success': False, 'error': 'Flash operation failed'}
        
        # Small delay to ensure device is properly released
        time.sleep(0.5)
        
        device_id = ip_addr or serial
        return {'device': device_id, 'success': True, 'error': None}
    except Exception as e:
        device_id = ip_addr or serial
        return {'device': device_id, 'success': False, 'error': str(e)}


def flash_devices(serial, ip_list, fw_file, mcu, programmer_type, log_level):
    """Flash one or multiple devices in parallel."""
    # Build device list
    devices = []
    if ip_list:
        devices = [{'serial': None, 'ip': ip} for ip in ip_list]
    elif serial and isinstance(serial, list):
        devices = [{'serial': s, 'ip': None} for s in serial]
    else:
        devices = [{'serial': serial, 'ip': None}]
    
    # Print device list
    device_names = []
    for d in devices:
        if d['ip']:
            device_names.append(str(d['ip']))
        elif d['serial'] is not None:
            device_names.append(f"serial {d['serial']}")
        else:
            device_names.append("auto-detected")
    print(f"Flashing {len(devices)} device(s): {', '.join(device_names)}")
    print(f"Firmware: {fw_file}\n")
    
    results = []
    if ip_list:
        # Parallel flashing for IPs
        from concurrent.futures import ProcessPoolExecutor, as_completed
        with ProcessPoolExecutor(max_workers=len(devices)) as executor:
            future_to_device = {
                executor.submit(flash_device_task, dev['serial'], dev['ip'], fw_file, mcu, programmer_type, log_level): dev
                for dev in devices
            }
            for future in as_completed(future_to_device):
                dev = future_to_device[future]
                try:
                    result = future.result(timeout=300)
                    results.append(result)
                    if result['success']:
                        print(f"✓ {result['device']}: Success")
                    else:
                        print(f"✗ {result['device']}: {result['error']}")
                except Exception as e:
                    device_id = dev['ip'] or dev['serial']
                    results.append({'device': device_id, 'success': False, 'error': str(e)})
                    print(f"✗ {device_id}: {e}")
    else:
        # Sequential flashing for serials
        for dev in devices:
            result = flash_device_task(dev['serial'], dev['ip'], fw_file, mcu, programmer_type, log_level)
            results.append(result)
            if result['success']:
                print(f"✓ {result['device']}: Success")
            else:
                print(f"✗ {result['device']}: {result['error']}")
    
    # Summary
    success_count = sum(1 for r in results if r['success'])
    fail_count = len(results) - success_count
    
    if len(devices) > 1:
        print(f"\n{'='*60}")
        print(f"Flashing completed: {success_count} successful, {fail_count} failed")
        print(f"{'='*60}")
    
    if fail_count > 0:
        if len(devices) > 1:
            print("\nFailed devices:")
            for r in results:
                if not r['success']:
                    print(f"  - {r['device']}: {r['error']}")
        sys.exit(1)

if __name__ == "__main__":
    main()
