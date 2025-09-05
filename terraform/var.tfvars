# AWS Configuration
aws_region = "us-east-1"

# Project Configuration
project_name = "fastmcp-server"
environment  = "prod"

# Container Configuration
container_port = 8000
cpu           = "512"
memory        = "1024"

# Scaling Configuration
desired_count = 2
min_capacity  = 1
max_capacity  = 10
