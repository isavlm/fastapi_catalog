#!/bin/bash

# Navigate to application directory
cd /home/ec2-user/Backend-Master-Challenge

# Install dependencies
pip3.11 install -r requirements.txt

# Install CloudWatch agent
sudo yum install -y amazon-cloudwatch-agent

# Copy CloudWatch config
sudo cp cloudwatch-config.json /opt/aws/amazon-cloudwatch-agent/etc/
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -s -c file:/opt/aws/amazon-cloudwatch-agent/etc/cloudwatch-config.json

# Start CloudWatch agent
sudo systemctl enable amazon-cloudwatch-agent
sudo systemctl start amazon-cloudwatch-agent

# Set permissions
sudo chown -R ec2-user:ec2-user /home/ec2-user/Backend-Master-Challenge
chmod +x /home/ec2-user/Backend-Master-Challenge/scripts/*.sh

# Copy systemd service file
sudo cp deployment/fastapi-catalog.service /etc/systemd/system/
sudo systemctl daemon-reload
