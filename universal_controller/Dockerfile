ARG BUILD_FROM
FROM $BUILD_FROM

# Install Node.js and npm
RUN apk add --no-cache \
    nodejs \
    npm

# Set working directory
WORKDIR /

# Copy package.json and install dependencies
COPY rootfs/app/package*.json ./app/
WORKDIR /app
RUN npm ci --production

# Copy application files
COPY rootfs/app/ ./

# Copy run script
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
