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
FROM ubuntu:latest

## Install required packages and JLink dependencies
RUN apt-get update && \
    apt-get install -y wget libusb-1.0-0 udev && \
    rm -rf /var/lib/apt/lists/*


# Copy both JLink packages into the container (they must be present in build context)
# COPY .github/workflows/JLink_Linux_${JLINK_VERSION}_x86_64.deb /tmp/JLink_Linux_${JLINK_VERSION}_x86_64.deb
# COPY .github/workflows/JLink_Linux_${JLINK_VERSION}_arm64.deb /tmp/JLink_Linux_${JLINK_VERSION}_arm64.deb
COPY JLink_x86_64.deb /tmp/JLink_x86_64.deb
COPY JLink_arm.deb /tmp/JLink_arm.deb
# Workaround: replace udevadm with a stub to avoid postinst errors in Docker
RUN if [ -f /bin/udevadm ]; then mv /bin/udevadm /bin/udevadm.real; fi && \
    echo '#!/bin/bash' > /bin/udevadm && \
    echo 'exit 0' >> /bin/udevadm && \
    chmod +x /bin/udevadm

# Install the appropriate JLink package depending on architecture (force install, then fix deps)
WORKDIR /tmp
RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then \
        dpkg --force-depends -i JLink_x86_64.deb || true && \
        rm JLink_x86_64.deb; \
    elif [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then \
        dpkg --force-depends -i JLink_arm.deb || true && \
        rm JLink_arm.deb; \
    fi
RUN if [ -f /bin/udevadm.real ]; then rm /bin/udevadm && mv /bin/udevadm.real /bin/udevadm; fi

# Add user (optional)
RUN useradd -ms /bin/bash jlink
USER jlink

WORKDIR /home/jlink

ENTRYPOINT ["/opt/SEGGER/JLink/JLinkRemoteServer"]