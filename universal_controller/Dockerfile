ARG BUILD_FROM=ghcr.io/hassio-addons/base/aarch64:15.0.7
FROM $BUILD_FROM

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install Node.js and npm
RUN \
    apk add --no-cache \
        nodejs=~20 \
        npm=~10

# Copy root filesystem
COPY rootfs /

# Install Node.js dependencies
WORKDIR /app
RUN npm install --omit=dev

# Build arguments
ARG BUILD_ARCH
ARG BUILD_DATE
ARG BUILD_DESCRIPTION
ARG BUILD_NAME
ARG BUILD_REF
ARG BUILD_REPOSITORY
ARG BUILD_VERSION

# Labels
LABEL \
    io.hass.name="${BUILD_NAME}" \
    io.hass.description="${BUILD_DESCRIPTION}" \
    io.hass.arch="${BUILD_ARCH}" \
    io.hass.type="addon" \
    io.hass.version=${BUILD_VERSION} \
    maintainer="Nogg-aholic" \
    org.opencontainers.image.title="${BUILD_NAME}" \
    org.opencontainers.image.description="${BUILD_DESCRIPTION}" \
    org.opencontainers.image.vendor="Home Assistant Community Add-ons" \
    org.opencontainers.image.authors="Nogg-aholic" \
    org.opencontainers.image.licenses="MIT" \
    org.opencontainers.image.url="https://github.com/Nogg-aholic/UniControl" \
    org.opencontainers.image.source="https://github.com/Nogg-aholic/UniControl" \
    org.opencontainers.image.documentation="https://github.com/Nogg-aholic/UniControl/blob/main/README.md" \
    org.opencontainers.image.created=${BUILD_DATE} \
    org.opencontainers.image.revision=${BUILD_REF} \
    org.opencontainers.image.version=${BUILD_VERSION}
