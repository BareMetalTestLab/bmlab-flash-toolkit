# Set JLink version as build argument
ARG JLINK_VERSION=V794e
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
COPY .github/workflows/JLink_Linux_${JLINK_VERSION}_x86_64.deb /tmp/JLink_Linux_${JLINK_VERSION}_x86_64.deb
COPY .github/workflows/JLink_Linux_${JLINK_VERSION}_arm64.deb /tmp/JLink_Linux_${JLINK_VERSION}_arm64.deb

# Install the appropriate JLink package depending on architecture (force install, then fix deps)
WORKDIR /tmp
RUN if [ "${ENABLE_JLINK}" = "true" ]; then \
        ARCH=$(uname -m) && \
        if [ "$ARCH" = "x86_64" ]; then \
            wget --post-data "accept_license_agreement=accepted" \
            https://www.segger.com/downloads/jlink/JLink_Linux_${JLINK_VERSION}_x86_64.deb \
            -O JLink.deb && \
            dpkg --force-depends -i JLink.deb && \
            rm JLink.deb; \
        elif [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then \
            wget --post-data "accept_license_agreement=accepted" \
            https://www.segger.com/downloads/jlink/JLink_Linux_${JLINK_VERSION}_arm64.deb \
            -O JLink.deb && \
            dpkg --force-depends -i JLink.deb && \
            rm JLink.deb; \
        fi && \
        echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="1366", MODE="0666"' > /etc/udev/rules.d/99-jlink.rules; \
    else \
        echo "Skipping J-Link installation (ENABLE_JLINK=${ENABLE_JLINK})"; \
    fi

# Add user (optional)
RUN useradd -ms /bin/bash jlink
USER jlink

WORKDIR /home/jlink

ENTRYPOINT ["/opt/SEGGER/JLink/JLinkRemoteServer"]