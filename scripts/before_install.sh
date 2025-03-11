#!/bin/bash

# Stop the existing service if running
sudo systemctl stop fastapi-catalog || true

# Clean up old deployment
rm -rf /home/ec2-user/Backend-Master-Challenge
