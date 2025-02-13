#!/bin/bash

# Navigate to application directory
cd /home/ec2-user/Backend-Master-Challenge

# Install/update dependencies
pip3.11 install -r requirements.txt

# Set permissions
chmod +x scripts/*.sh

# Copy systemd service file
sudo cp deployment/fastapi-catalog.service /etc/systemd/system/
sudo systemctl daemon-reload
