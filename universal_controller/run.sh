#!/usr/bin/with-contenv bashio

# Print startup message
bashio::log.info "Starting Universal Controller..."

# Change to app directory
cd /app

# Start the Node.js server
bashio::log.info "Starting Node.js server on port 8099..."
exec node server.js
