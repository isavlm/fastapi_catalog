#!/bin/bash

# Check if service is running
if ! systemctl is-active --quiet fastapi-catalog; then
    echo "Service is not running"
    exit 1
fi

# Check if API is responding
if ! curl -s http://localhost:8000/health_check/ | grep -q "OK"; then
    echo "API health check failed"
    exit 1
fi

echo "Service validation successful"
exit 0
