"""Programmer constants and configuration."""

# Supported programmers
PROGRAMMER_JLINK = "jlink"

# List of all supported programmers
SUPPORTED_PROGRAMMERS = [
    PROGRAMMER_JLINK,
    # Future: "stlink", "openocd", etc.
]

# Default programmer
DEFAULT_PROGRAMMER = PROGRAMMER_JLINK



LOG_LEVEL_INFO = 'INFO'
LOG_LEVEL_ERROR = 'ERROR'
LOG_LEVEL_DEBUG = 'DEBUG'
LOG_LEVEL_WARNING = 'WARNING'

LOG_LEVELS = [
    LOG_LEVEL_INFO,
    LOG_LEVEL_ERROR,
    LOG_LEVEL_DEBUG,
    LOG_LEVEL_WARNING
]

DEFAULT_LOG_LEVEL = LOG_LEVEL_WARNING