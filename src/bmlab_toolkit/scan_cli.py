"""
Device Scanner CLI

Command-line interface for scanning and listing available programmers.
"""

import sys
import argparse
import logging
from .constants import SUPPORTED_PROGRAMMERS, DEFAULT_PROGRAMMER, PROGRAMMER_JLINK
from .jlink_programmer import JLinkProgrammer


def main():
    """Main entry point for bmlab-scan command."""
    parser = argparse.ArgumentParser(
        description='Scan and list available programmers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan for JLink programmers
  bmlab-scan

  # Scan with debug output
  bmlab-scan --log-level DEBUG
        """
    )
    
    parser.add_argument(
        '--programmer', '-p',
        type=str,
        default=DEFAULT_PROGRAMMER,
        choices=SUPPORTED_PROGRAMMERS,
        help=f'Programmer type to scan for (default: {DEFAULT_PROGRAMMER})'
    )
    
    parser.add_argument(
        '--log-level', '-l',
        type=str,
        default='WARNING',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Set logging level (default: WARNING)'
    )
    
    args = parser.parse_args()
    
    try:
        # Convert log level string to logging constant
        log_level = getattr(logging, args.log_level.upper())
        
        # Configure logging
        logging.basicConfig(level=log_level, format='%(levelname)s - %(message)s')
        
        if args.programmer.lower() == PROGRAMMER_JLINK:
            devices = JLinkProgrammer.scan()
            
            if not devices:
                print("No JLink devices found.")
                sys.exit(1)
            
            print(f"Found {len(devices)} JLink device(s):\n")
            for i, dev in enumerate(devices):
                product = dev.get('product', 'Unknown')
                target = dev.get('target', 'Not detected')
                serial = dev['serial']
                
                print(f"[{i}] JLink Programmer")
                print(f"    Serial:  {serial}")
                print(f"    Product: {product}")
                print(f"    Target:  {target}")
                print()
        else:
            print(f"Error: Programmer '{args.programmer}' is not yet implemented")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\nScan cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
