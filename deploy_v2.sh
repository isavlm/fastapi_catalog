#!/bin/bash

# Update system and install dependencies
sudo yum update -y
sudo yum install -y python3-pip git postgresql15

# Create application directory
sudo mkdir -p /opt/fastapi-catalog
sudo chown ec2-user:ec2-user /opt/fastapi-catalog

# Extract the application
cd /opt/fastapi-catalog
tar xzf ~/Backend-Master-Challenge.tar.gz
mv Backend-Master-Challenge/* .
mv Backend-Master-Challenge/.* . 2>/dev/null || true
rmdir Backend-Master-Challenge

# Install Python dependencies
pip3 install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv

# Create systemd service file
sudo tee /etc/systemd/system/fastapi-catalog.service << EOF
[Unit]
Description=FastAPI Catalog Service
After=network.target

[Service]
User=ec2-user
Group=ec2-user
WorkingDirectory=/opt/fastapi-catalog
Environment="PATH=/home/ec2-user/.local/bin:/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin"
Environment="PYTHONPATH=/opt/fastapi-catalog"
Environment="DATABASE_URL=postgresql://catalog_admin:catalog_password_123@catalog-db.c3ggssye4sbv.us-west-2.rds.amazonaws.com:5432/catalogdb"
Environment="HOST=0.0.0.0"
Environment="PORT=8000"
Environment="ENVIRONMENT=production"
ExecStart=/home/ec2-user/.local/bin/uvicorn application:application --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and start service
sudo systemctl daemon-reload
sudo systemctl enable fastapi-catalog
sudo systemctl start fastapi-catalog

# Show service status
sudo systemctl status fastapi-catalog
