##
# Usage example:
# Build:
#   docker build -t my-jlink-image -f jlinkRemoteServerEmu.dockerfile .
# Run (with USB access and custom network):
#   docker network create --subnet=192.168.100.0/24 jlink-net
#   docker run -d --rm --name jlink1 --network jlink-net --ip 192.168.100.10 \
#     --device=/dev/bus/usb:/dev/bus/usb \
#     my-jlink-image \
#     -select usb=SERIAL1 -device STM32F103RE -endian little -speed 4000 -if swd
# Replace SERIAL1 with your J-Link serial number.
#
FROM ubuntu:22.04

## Install required packages and JLink dependencies
RUN apt-get update && \
    apt-get install -y wget libusb-1.0-0 && \
    rm -rf /var/lib/apt/lists/*


# Copy both JLink packages into the container (they must be present in build context)
COPY .github/workflows/JLink_Linux_V896_x86_64.deb /tmp/JLink_Linux_V896_x86_64.deb
COPY .github/workflows/JLink_Linux_V896_arm64.deb /tmp/JLink_Linux_V896_arm64.deb

# Install the appropriate JLink package depending on architecture (force install, then fix deps)
RUN arch=$(uname -m) && \
    if [ "$arch" = "x86_64" ]; then \
        dpkg --force-depends -i /tmp/JLink_Linux_V896_x86_64.deb; \
    elif [ "$arch" = "aarch64" ] || [ "$arch" = "arm64" ]; then \
        dpkg --force-depends -i /tmp/JLink_Linux_V896_arm64.deb; \
    else \
        echo "Unsupported architecture: $arch" && exit 1; \
    fi && \
    apt-get install -f -y

# Add user (optional)
RUN useradd -ms /bin/bash jlink
USER jlink

WORKDIR /home/jlink

ENTRYPOINT ["/opt/SEGGER/JLink/JLinkRemoteServer"]