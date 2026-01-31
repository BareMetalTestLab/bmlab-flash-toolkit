import argparse
import argcomplete

from . import rtt_cli
from . import scan_cli
from . import erase_cli
from . import flash_cli
from .constants import SUPPORTED_PROGRAMMERS, DEFAULT_PROGRAMMER, LOG_LEVELS, DEFAULT_LOG_LEVEL


def create_scan_parser(subparser: argparse._SubParsersAction):
    scan_parser = subparser.add_parser(
        'scan', 
        help='Scan and list available programmers'
    )

    scan_parser.add_argument(
        '--network', '-n',
        type=str,
        default=None,
        help='Network to scan for JLink Remote Servers (e.g., 192.168.1.0/24)'
    )
    
    scan_parser.add_argument(
        '--start-ip',
        type=int,
        default=None,
        help='Starting last octet for IP range (e.g., 100 for x.x.x.100)'
    )
    
    scan_parser.add_argument(
        '--end-ip',
        type=int,
        default=None,
        help='Ending last octet for IP range (e.g., 150 for x.x.x.150)'
    )
    
    scan_parser.add_argument(
        '--programmer', '-p',
        type=str,
        default=DEFAULT_PROGRAMMER,
        choices=SUPPORTED_PROGRAMMERS,
        help=f'Programmer type to scan for (default: {DEFAULT_PROGRAMMER})'
    )
    
    scan_parser.add_argument(
        '--log-level', '-l',
        type=str,
        default=DEFAULT_LOG_LEVEL,
        choices= LOG_LEVELS,
        help=f'Set logging level (default: {DEFAULT_LOG_LEVEL})'
    )


def create_erase_parser(subparser: argparse._SubParsersAction):
    erase_parser = subparser.add_parser(
        'erase', 
        help='Erase flash memory of embedded devices'
    ) 

    erase_parser.add_argument(
        '--serial', '-s', 
        type=int, 
        nargs='+', 
        default=None,
        help='JLink serial number(s) (can specify multiple for sequential erase, or leave empty for auto-detect)'
        )
    
    erase_parser.add_argument(
        '--mcu', '-m', 
        type=str, 
        default=None,
        help='MCU name (e.g., STM32F765ZG). Auto-detects if not provided.'
        )
    
    erase_parser.add_argument(
        '--ip', 
        type=str, 
        nargs='+', 
        default=None,
        help='JLink IP address(es) for network connection (can specify multiple for parallel erase)'
        )
    
    erase_parser.add_argument(
        '--log-level', '-l',
        type=str, 
        default=DEFAULT_LOG_LEVEL,
        choices=LOG_LEVELS,
        help=f'Set logging level (default: {DEFAULT_LOG_LEVEL})'
        )


def create_rtt_parser(subparser: argparse._SubParsersAction):
    
    rtt_parser = subparser.add_parser(
        'rtt', 
        help='Connect to RTT for real-time data transfer'
    ) 
       
    rtt_parser.add_argument(
        '--serial', '-s', 
        type=int, nargs='+', 
        default=None,
        help='Programmer serial number(s) (auto-detect if not provided)'
        )
    
    rtt_parser.add_argument(
        '--programmer', '-p',
        type=str, default=DEFAULT_PROGRAMMER,
        choices=SUPPORTED_PROGRAMMERS,
        help=f'Programmer type (default: {DEFAULT_PROGRAMMER})'
        )
    
    rtt_parser.add_argument(
        '--ip', 
        type=str, 
        nargs='+', 
        default=None,
        help='JLink IP address(es) for network connection (can specify multiple)'
        )
    
    rtt_parser.add_argument(
        '--output-dir',
        type=str, default=None,
        help='Output directory for RTT logs (required for multiple devices)'
        )
    
    rtt_parser.add_argument(
        '--mcu', '-m', 
        type=str, 
        default=None,
        help='MCU name (e.g., STM32F765ZG). Auto-detects if not provided. Not used with --ip.'
        )
    
    rtt_parser.add_argument(
        '--reset', 
        dest='reset', 
        action='store_true', 
        default=True,
        help='Reset target after connection (default: True)'
        )
    
    rtt_parser.add_argument(
        '--no-reset', 
        dest='reset',
        action='store_false',
        help='Do not reset target after connection'
        )
    
    rtt_parser.add_argument(
        '--timeout', '-t',
        type=float,
        default=10.0,
        help='Read timeout in seconds. 0 means read until interrupted (default: 10.0)'
        )
    
    rtt_parser.add_argument(
        '--msg', 
        type=str, 
        default=None,
        help='Message to send via RTT after connection'
        )
    
    rtt_parser.add_argument(
        '--msg-timeout', 
        type=float, 
        default=0.5,
        help='Delay in seconds before sending message (default: 0.5)'
        )
    
    rtt_parser.add_argument(
        '--msg-retries',
        type=int,
        default=10,
        help='Number of retries for sending message (default: 10)'
        )
    
    rtt_parser.add_argument(
        '--log-level', '-l', 
        type=str, 
        default=DEFAULT_LOG_LEVEL,
        choices=LOG_LEVELS,
        help=f'Set logging level (default: {DEFAULT_LOG_LEVEL})'
        )


def create_flash_parser(subparser: argparse._SubParsersAction):
    flash_parser = subparser.add_parser(
        'flash', 
        help='Flash embedded devices and manage programmers'
    )

    flash_parser.add_argument(
        "firmware_file",
        type=str,
        help="Path to firmware file (.hex or .bin)"
    )
    
    flash_parser.add_argument(
        "--serial", "-s",
        type=int,
        nargs='+',
        default=None,
        help="Programmer serial number(s) (can specify multiple for parallel flashing, or leave empty for auto-detect)"
    )
    
    flash_parser.add_argument(
        "--ip",
        type=str,
        nargs='+',
        default=None,
        help="JLink IP address(es) for network connection (e.g., 192.168.1.100 or multiple: 192.168.1.100 192.168.1.101)"
    )
    
    flash_parser.add_argument(
        "--mcu",
        type=str,
        default=None,
        help="MCU name (e.g., STM32F765ZG). If not provided, will auto-detect"
    )
    
    flash_parser.add_argument(
        "--programmer", "-p",
        type=str,
        default=DEFAULT_PROGRAMMER,
        choices=SUPPORTED_PROGRAMMERS,
        help=f"Programmer type (default: {DEFAULT_PROGRAMMER})"
    )
    
    flash_parser.add_argument(
        "--log-level", "-l",
        type=str,
        default=DEFAULT_LOG_LEVEL,
        choices=LOG_LEVELS,
        help=f"Set logging level (default: {DEFAULT_LOG_LEVEL})"
    )


def main():
    
    parser = argparse.ArgumentParser(description="BMLab-toolkit")
    subparser = parser.add_subparsers(title='Available commands', dest='command', metavar='Command', help='Command descriptions', required=True)
    create_rtt_parser(subparser)
    create_scan_parser(subparser)
    create_erase_parser(subparser)
    create_flash_parser(subparser)
    # flash_parser = subparsers.add_parser('flash', help='Flash embedded devices and manage programmers')


    # Включаем автодополнение
    argcomplete.autocomplete(parser)
    
    # Парсим аргументы
    args = parser.parse_args()
    if args.command == 'rtt':
        rtt_cli.main(args)
    elif args.command == 'scan':
        scan_cli.main(args)
    elif args.command == 'erase':
        erase_cli.main(args)
    elif args.command == 'flash':
        flash_cli.main(args)
    else:
        print('Unknown command')
