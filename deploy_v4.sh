#!/bin/bash

# Update system and install dependencies
sudo yum update -y
sudo yum install -y python3-pip git postgresql15

# Clean up and recreate application directory
sudo rm -rf /opt/fastapi-catalog/*
sudo rm -rf /opt/fastapi-catalog/.[!.]*
sudo mkdir -p /opt/fastapi-catalog
sudo chown ec2-user:ec2-user /opt/fastapi-catalog

# Extract the application
cd /opt/fastapi-catalog
tar xzf ~/Backend-Master-Challenge.tar.gz --strip-components=1

# Install Python dependencies globally
sudo pip3 install fastapi uvicorn[standard] sqlalchemy psycopg2-binary python-dotenv pydantic

# Create systemd service file
sudo tee /etc/systemd/system/fastapi-catalog.service << EOF
[Unit]
Description=FastAPI Catalog Service
After=network.target

[Service]
User=ec2-user
Group=ec2-user
WorkingDirectory=/opt/fastapi-catalog
Environment="PATH=/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin"
Environment="PYTHONPATH=/opt/fastapi-catalog"
Environment="DATABASE_URL=postgresql://catalog_admin:catalog_password_123@catalog-db.c3ggssye4sbv.us-west-2.rds.amazonaws.com:5432/catalogdb"
Environment="HOST=0.0.0.0"
Environment="PORT=8000"
Environment="ENVIRONMENT=production"
ExecStart=/usr/local/bin/uvicorn application:application --host 0.0.0.0 --port 8000 --log-level info

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and start service
sudo systemctl daemon-reload
sudo systemctl enable fastapi-catalog
sudo systemctl restart fastapi-catalog

# Show service status and logs
sudo systemctl status fastapi-catalog
sudo journalctl -u fastapi-catalog -n 50
