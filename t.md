User: Deployment Self-Hosted Remote MCP

Deploy your FastMCP server as a remote MCP service accessible via URL STDIO transport is perfect for local development and desktop applications. But to unlock the full potential of MCP—centralized services, multi-client access, and network availability—you need remote HTTP deployment. This guide walks you through deploying your FastMCP server as a remote MCP service that’s accessible via a URL. Once deployed, your MCP server will be available over the network, allowing multiple clients to connect simultaneously and enabling integration with cloud-based LLM applications. This guide focuses specifically on remote MCP deployment, not local STDIO servers. ​ Choosing Your Approach FastMCP provides two ways to deploy your server as an HTTP service. Understanding the trade-offs helps you choose the right approach for your needs. The direct HTTP server approach is simpler and perfect for getting started quickly. You modify your server’s run() method to use HTTP transport, and FastMCP handles all the web server configuration. This approach works well for standalone deployments where you want your MCP server to be the only service running on a port. The ASGI application approach gives you more control and flexibility. Instead of running the server directly, you create an ASGI application that can be served by production-grade servers like Uvicorn or Gunicorn. This approach is better when you need advanced server features like multiple workers, custom middleware, or when you’re integrating with existing web applications. ​ Direct HTTP Server The simplest way to get your MCP server online is to use the built-in run() method with HTTP transport. This approach handles all the server configuration for you and is ideal when you want a standalone MCP server without additional complexity. server.py Copy

from fastmcp import FastMCP

mcp = FastMCP("My Server")

@mcp.tool def process_data(input: str) -> str: """Process data on the server""" return f"Processed: {input}"

if name == "main": mcp.run(transport="http", host="0.0.0.0", port=8000)

Run your server with a simple Python command: Copy

python server.py

Your server is now accessible at http://localhost:8000/mcp/ (or use your server’s actual IP address for remote access). This approach is ideal when you want to get online quickly with minimal configuration. It’s perfect for internal tools, development environments, or simple deployments where you don’t need advanced server features. The built-in server handles all the HTTP details, letting you focus on your MCP implementation. ​ ASGI Application For production deployments, you’ll often want more control over how your server runs. FastMCP can create a standard ASGI application that works with any ASGI server like Uvicorn, Gunicorn, or Hypercorn. This approach is particularly useful when you need to configure advanced server options, run multiple workers, or integrate with existing infrastructure. app.py Copy

from fastmcp import FastMCP

mcp = FastMCP("My Server")

@mcp.tool def process_data(input: str) -> str: """Process data on the server""" return f"Processed: {input}"
Create ASGI application

app = mcp.http_app()

Run with any ASGI server - here’s an example with Uvicorn: Copy

uvicorn app:app --host 0.0.0.0 --port 8000

Your server is accessible at the same URL: http://localhost:8000/mcp/ (or use your server’s actual IP address for remote access). The ASGI approach shines in production environments where you need reliability and performance. You can run multiple worker processes to handle concurrent requests, add custom middleware for logging or monitoring, integrate with existing deployment pipelines, or mount your MCP server as part of a larger application. This flexibility makes it the preferred choice for serious deployments. ​ Configuring Your Server ​ Custom Path By default, your MCP server is accessible at /mcp/ on your domain. You can customize this path to fit your URL structure or avoid conflicts with existing endpoints. This is particularly useful when integrating MCP into an existing application or following specific API conventions. Copy
Option 1: With mcp.run()

mcp.run(transport="http", host="0.0.0.0", port=8000, path="/api/mcp/")
Option 2: With ASGI app

app = mcp.http_app(path="/api/mcp/")

Now your server is accessible at http://localhost:8000/api/mcp/. ​ Authentication Authentication is highly recommended for remote MCP servers. Some LLM clients require authentication for remote servers and will refuse to connect without it. FastMCP supports multiple authentication methods to secure your remote server. See the Authentication Overview for complete configuration options including Bearer tokens, JWT, and OAuth. ​ Health Checks Health check endpoints are essential for monitoring your deployed server and ensuring it’s responding correctly. FastMCP allows you to add custom routes alongside your MCP endpoints, making it easy to implement health checks that work with both deployment approaches. Copy

from starlette.responses import JSONResponse

@mcp.custom_route("/health", methods=["GET"]) async def health_check(request): return JSONResponse({"status": "healthy", "service": "mcp-server"})

This health endpoint will be available at http://localhost:8000/health and can be used by load balancers, monitoring systems, or deployment platforms to verify your server is running. ​ Integration with Web Frameworks If you already have a web application running, you can add MCP capabilities by mounting a FastMCP server as a sub-application. This allows you to expose MCP tools alongside your existing API endpoints, sharing the same domain and infrastructure. The MCP server becomes just another route in your application, making it easy to manage and deploy. For detailed integration guides, see:

FastAPI Integration
ASGI / Starlette Integration

Here’s a quick example showing how to add MCP to an existing FastAPI application: Copy

from fastapi import FastAPI from fastmcp import FastMCP
Your existing API

api = FastAPI()

@api.get("/api/status") def status(): return {"status": "ok"}
Create your MCP server

mcp = FastMCP("API Tools")

@mcp.tool def query_database(query: str) -> dict: """Run a database query""" return {"result": "data"}
Mount MCP at /mcp

api.mount("/mcp", mcp.http_app())
Run with: uvicorn app:api --host 0.0.0.0 --port 8000

Your existing API remains at http://localhost:8000/api/ while MCP is available at http://localhost:8000/mcp/. ​ Production Deployment ​ Running with Uvicorn When deploying to production, you’ll want to optimize your server for performance and reliability. Uvicorn provides several options to improve your server’s capabilities, including running multiple worker processes to handle concurrent requests and enabling enhanced logging for monitoring. Copy
Install uvicorn with standard extras for better performance

pip install 'uvicorn[standard]'
Run with multiple workers for better concurrency

uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
Enable detailed logging for monitoring

uvicorn app:app --host 0.0.0.0 --port 8000 --log-level info

​ Environment Variables Production deployments should never hardcode sensitive information like API keys or authentication tokens. Instead, use environment variables to configure your server at runtime. This keeps your code secure and makes it easy to deploy the same code to different environments with different configurations. Here’s an example using bearer token authentication (though OAuth is recommended for production): Copy

import os from fastmcp import FastMCP from fastmcp.server.auth import BearerTokenAuth
Read configuration from environment

auth_token = os.environ.get("MCP_AUTH_TOKEN") if auth_token: auth = BearerTokenAuth(token=auth_token) mcp = FastMCP("Production Server", auth=auth) else: mcp = FastMCP("Production Server")

app = mcp.http_app()

Deploy with your secrets safely stored in environment variables: Copy

MCP_AUTH_TOKEN=secret uvicorn app:app --host 0.0.0.0 --port 8000

​ Testing Your Deployment Once your server is deployed, you’ll need to verify it’s accessible and functioning correctly. For comprehensive testing strategies including connectivity tests, client testing, and authentication testing, see the Testing Your Server guide. ​ Hosting Your Server This guide has shown you how to create an HTTP-accessible MCP server, but you’ll still need a hosting provider to make it available on the internet. Your FastMCP server can run anywhere that supports Python web applications:

Cloud VMs (AWS EC2, Google Compute Engine, Azure VMs)
Container platforms (Cloud Run, Container Instances, ECS)
Platform-as-a-Service (Railway, Render, Vercel)
Edge platforms (Cloudflare Workers)
Kubernetes clusters (self-managed or managed)

The key requirements are Python 3.10+ support and the ability to expose an HTTP port. Most providers will require you to package your server (requirements.txt, Dockerfile, etc.) according to their deployment format. For managed, zero-configuration deployment, see FastMCP Cloud.

Based on that provided documentation, create the terraform configuration to deploy a simple mcp server on aws I want it to be built using docker to be stored in ecs and run using fargate, in terms of networking make it simple by only running the task in a single public subnet
Model: I'll create a Terraform configuration to deploy an MCP server on AWS using ECS Fargate with Docker. This setup will use a single public subnet for simplicity.

## Directory Structure

```
mcp-server-deployment/
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── terraform.tfvars.example
├── app/
│   ├── server.py
│   ├── requirements.txt
│   └── Dockerfile
└── README.md
```

## Application Files

### `app/server.py`
```python
import os
from fastmcp import FastMCP
from fastmcp.server.auth import BearerTokenAuth

# Read configuration from environment
auth_token = os.environ.get("MCP_AUTH_TOKEN")
server_name = os.environ.get("MCP_SERVER_NAME", "Remote MCP Server")

# Initialize server with optional authentication
if auth_token:
    auth = BearerTokenAuth(token=auth_token)
    mcp = FastMCP(server_name, auth=auth)
else:
    mcp = FastMCP(server_name)

# Example tools
@mcp.tool
def process_data(input: str) -> str:
    """Process data on the server"""
    return f"Processed: {input}"

@mcp.tool
def get_server_info() -> dict:
    """Get information about the server"""
    return {
        "name": server_name,
        "version": "1.0.0",
        "status": "running"
    }

# Health check endpoint
from starlette.responses import JSONResponse

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    return JSONResponse({
        "status": "healthy",
        "service": "mcp-server"
    })

# Create ASGI application for production deployment
app = mcp.http_app()
```

### `app/requirements.txt`
```txt
fastmcp>=0.1.0
uvicorn[standard]>=0.24.0
```

### `app/Dockerfile`
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY server.py .

# Run with uvicorn
EXPOSE 8000
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

## Terraform Configuration

### `terraform/variables.tf`
```hcl
variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "mcp-server"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "container_port" {
  description = "Port the container listens on"
  type        = number
  default     = 8000
}

variable "task_cpu" {
  description = "CPU units for the task (256, 512, 1024, 2048, 4096)"
  type        = string
  default     = "256"
}

variable "task_memory" {
  description = "Memory for the task in MB (512, 1024, 2048, etc.)"
  type        = string
  default     = "512"
}

variable "desired_count" {
  description = "Number of tasks to run"
  type        = number
  default     = 1
}

variable "mcp_auth_token" {
  description = "Bearer token for MCP authentication"
  type        = string
  sensitive   = true
  default     = ""
}

variable "mcp_server_name" {
  description = "Name for the MCP server"
  type        = string
  default     = "Remote MCP Server"
}

variable "availability_zone" {
  description = "Availability zone for the subnet"
  type        = string
  default     = "us-east-1a"
}
```

### `terraform/main.tf`
```hcl
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC and Networking
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "${var.project_name}-vpc"
    Environment = var.environment
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name        = "${var.project_name}-igw"
    Environment = var.environment
  }
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = var.availability_zone
  map_public_ip_on_launch = true

  tags = {
    Name        = "${var.project_name}-public-subnet"
    Environment = var.environment
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name        = "${var.project_name}-public-rt"
    Environment = var.environment
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# Security Group
resource "aws_security_group" "ecs_tasks" {
  name        = "${var.project_name}-ecs-tasks-sg"
  description = "Security group for ECS tasks"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "Allow HTTP traffic"
    from_port   = var.container_port
    to_port     = var.container_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.project_name}-ecs-tasks-sg"
    Environment = var.environment
  }
}

# ECR Repository
resource "aws_ecr_repository" "mcp_server" {
  name                 = "${var.project_name}-repo"
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name        = "${var.project_name}-ecr"
    Environment = var.environment
  }
}

# IAM Roles
resource "aws_iam_role" "ecs_task_execution" {
  name = "${var.project_name}-ecs-task-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-ecs-execution-role"
    Environment = var.environment
  }
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "ecs_task" {
  name = "${var.project_name}-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-ecs-task-role"
    Environment = var.environment
  }
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "ecs" {
  name              = "/ecs/${var.project_name}"
  retention_in_days = 7

  tags = {
    Name        = "${var.project_name}-logs"
    Environment = var.environment
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Name        = "${var.project_name}-cluster"
    Environment = var.environment
  }
}

# ECS Task Definition
resource "aws_ecs_task_definition" "mcp_server" {
  family                   = "${var.project_name}-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.task_cpu
  memory                   = var.task_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name  = var.project_name
      image = "${aws_ecr_repository.mcp_server.repository_url}:latest"
      
      essential = true
      
      portMappings = [
        {
          containerPort = var.container_port
          protocol      = "tcp"
        }
      ]
      
      environment = [
        {
          name  = "MCP_SERVER_NAME"
          value = var.mcp_server_name
        }
      ]
      
      secrets = var.mcp_auth_token != "" ? [
        {
          name      = "MCP_AUTH_TOKEN"
          valueFrom = aws_ssm_parameter.mcp_auth_token[0].arn
        }
      ] : []
      
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
      
      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:${var.container_port}/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])

  tags = {
    Name        = "${var.project_name}-task"
    Environment = var.environment
  }
}

# SSM Parameter for auth token (if provided)
resource "aws_ssm_parameter" "mcp_auth_token" {
  count = var.mcp_auth_token != "" ? 1 : 0
  
  name  = "/${var.project_name}/${var.environment}/mcp-auth-token"
  type  = "SecureString"
  value = var.mcp_auth_token

  tags = {
    Name        = "${var.project_name}-auth-token"
    Environment = var.environment
  }
}

# IAM policy for SSM parameter access
resource "aws_iam_role_policy" "ecs_ssm_access" {
  count = var.mcp_auth_token != "" ? 1 : 0
  
  name = "${var.project_name}-ssm-access"
  role = aws_iam_role.ecs_task_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameters",
          "ssm:GetParameter"
        ]
        Resource = aws_ssm_parameter.mcp_auth_token[0].arn
      }
    ]
  })
}

# ECS Service
resource "aws_ecs_service" "mcp_server" {
  name            = "${var.project_name}-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.mcp_server.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [aws_subnet.public.id]
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = true
  }

  tags = {
    Name        = "${var.project_name}-service"
    Environment = var.environment
  }
}
```

### `terraform/outputs.tf`
```hcl
output "ecr_repository_url" {
  description = "URL of the ECR repository"
  value       = aws_ecr_repository.mcp_server.repository_url
}

output "ecr_repository_name" {
  description = "Name of the ECR repository"
  value       = aws_ecr_repository.mcp_server.name
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  description = "Name of the ECS service"
  value       = aws_ecs_service.mcp_server.name
}

output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "public_subnet_id" {
  description = "ID of the public subnet"
  value       = aws_subnet.public.id
}

output "mcp_server_url" {
  description = "Note: Task IP is dynamic. Check ECS console for current task IP"
  value       = "http://<TASK_PUBLIC_IP>:${var.container_port}/mcp/"
}

output "health_check_url" {
  description = "Health check endpoint (replace with actual task IP)"
  value       = "http://<TASK_PUBLIC_IP>:${var.container_port}/health"
}
```

### `terraform/terraform.tfvars.example`
```hcl
aws_region      = "ca-central"
project_name    = "mcp-server"
environment     = "production"
task_cpu        = "256"
task_memory     = "512"
desired_count   = 1
mcp_auth_token  = "your-secret-token-here"  # Optional but recommended
mcp_server_name = "My Remote MCP Server"
```

## Deployment Script

### `deploy.sh`
```bash
#!/bin/bash

set -e

# Configuration
AWS_REGION="us-east-1"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPO_NAME="mcp-server-repo"
IMAGE_TAG="latest"

echo "🚀 Starting MCP Server deployment..."

# Step 1: Build Docker image
echo "📦 Building Docker image..."
cd app
docker build -t ${ECR_REPO_NAME}:${IMAGE_TAG} .

# Step 2: Login to ECR
echo "🔐 Logging into ECR..."
aws ecr get-login-password --region ${AWS_REGION} | \
  docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# Step 3: Tag and push image
echo "⬆️ Pushing image to ECR..."
docker tag ${ECR_REPO_NAME}:${IMAGE_TAG} \
  ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}:${IMAGE_TAG}

docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}:${IMAGE_TAG}

# Step 4: Deploy with Terraform
echo "🏗️ Deploying infrastructure with Terraform..."
cd ../terraform
terraform init
terraform apply -auto-approve

# Step 5: Get task IP
echo "📍 Getting task public IP..."
CLUSTER_NAME=$(terraform output -raw ecs_cluster_name)
SERVICE_NAME=$(terraform output -raw ecs_service_name)

# Wait for service to stabilize
echo "⏳ Waiting for service to stabilize..."
aws ecs wait services-stable --cluster ${CLUSTER_NAME} --services ${SERVICE_NAME} --region ${AWS_REGION}

# Get task ARN
TASK_ARN=$(aws ecs list-tasks --cluster ${CLUSTER_NAME} --service-name ${SERVICE_NAME} --region ${AWS_REGION} --query 'taskArns[0]' --output text)

# Get ENI ID
ENI_ID=$(aws ecs describe-tasks --cluster ${CLUSTER_NAME} --tasks ${TASK_ARN} --region ${AWS_REGION} \
  --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' --output text)

# Get public IP
PUBLIC_IP=$(aws ec2 describe-network-interfaces --network-interface-ids ${ENI_ID} --region ${AWS_REGION} \
  --query 'NetworkInterfaces[0].Association.PublicIp' --output text)

echo "✅ Deployment complete!"
echo "🌐 MCP Server URL: http://${PUBLIC_IP}:8000/mcp/"
echo "💚 Health Check: http://${PUBLIC_IP}:8000/health"
```

## README.md
```markdown
# MCP Server AWS Deployment

This project deploys a FastMCP server to AWS using ECS Fargate with Docker containers.

## Prerequisites

- AWS CLI configured with appropriate credentials
- Terraform >= 1.0
- Docker installed locally
- Python 3.11+ (for local development)

## Quick Start

1. **Clone and setup**:
   ```bash
   git clone <repository>
   cd mcp-server-deployment
   ```

2. **Configure Terraform variables**:
   ```bash
   cd terraform
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your settings
   ```

3. **Deploy**:
   ```bash
   # Make deploy script executable
   chmod +x deploy.sh
   
   # Run deployment
   ./deploy.sh
   ```

## Manual Deployment Steps

1. **Build and push Docker image**:
   ```bash
   cd app
   docker build -t mcp-server:latest .
   
   # Login to ECR
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
   
   # Tag and push
   docker tag mcp-server:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/mcp-server-repo:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/mcp-server-repo:latest
   ```

2. **Deploy infrastructure**:
   ```bash
   cd terraform
   terraform init
   terraform plan
   terraform apply
   ```

3. **Get task public IP**:
   ```bash
   # Get task ARN
   aws ecs list-tasks --cluster mcp-server-cluster --service-name mcp-server-service
   
   # Describe task to get ENI
   aws ecs describe-tasks --cluster mcp-server-cluster --tasks <task-arn>
   
   # Get public IP from ENI
   aws ec2 describe-network-interfaces --network-interface-ids <eni-id>
   ```

## Accessing Your Server

Once deployed, your MCP server will be available at:
- MCP Endpoint: `http://<TASK_PUBLIC_IP>:8000/mcp/`
- Health Check: `http://<TASK_PUBLIC_IP>:8000/health`

## Configuration

### Environment Variables
- `MCP_AUTH_TOKEN`: Bearer token for authentication (stored in AWS SSM)
- `MCP_SERVER_NAME`: Name of your MCP server

### Terraform Variables
See `terraform/variables.tf` for all available configuration options.

## Updating the Server

To update your server code:
1. Modify `app/server.py`
2. Rebuild and push the Docker image
3. Force a new deployment:
   ```bash
   aws ecs update-service --cluster mcp-server-cluster --service mcp-server-service --force-new-deployment
   ```

## Monitoring

- CloudWatch Logs: `/ecs/mcp-server`
- ECS Console: View task status and metrics
- Health endpoint: `http://<IP>:8000/health`

## Security Notes

- The server runs in a public subnet with a public IP for simplicity
- Authentication is recommended for production use
- Consider using an Application Load Balancer for production
- Use HTTPS in production (add ACM certificate and ALB)

## Cleanup

To destroy all resources:
```bash
cd terraform
terraform destroy
```

## Cost Considerations

- ECS Fargate: ~$0.04/hour for 0.25 vCPU + 0.5GB RAM
- Data transfer: $0.09/GB outbound
- CloudWatch Logs: Minimal cost for low volume

## Troubleshooting

1. **Task fails to start**: Check CloudWatch logs
2. **Cannot connect**: Verify security group allows port 8000
3. **Authentication issues**: Verify SSM parameter is set correctly
```

This configuration provides:

1. **Simple networking**: Single public subnet with internet gateway
2. **Docker containerization**: Dockerfile for the MCP server
3. **ECS Fargate**: Serverless container hosting
4. **Security**: Optional bearer token authentication via SSM Parameter Store
5. **Monitoring**: CloudWatch logs and health checks
6. **Easy deployment**: Automated deployment script

The setup is production-ready but kept simple as requested. For production use, consider adding:
- Application Load Balancer for stable endpoint
- Auto-scaling based on CPU/memory
- Multiple availability zones for high availability
- HTTPS termination with ACM certificates
- VPN or private connectivity options
User: #!/bin/bash

set -e

# Configuration
AWS_REGION="us-east-1"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPO_NAME="mcp-server-repo"
IMAGE_TAG="latest"

echo "🚀 Starting MCP Server deployment..."

# Step 1: Build Docker image
echo "📦 Building Docker image..."
cd app
docker build -t ${ECR_REPO_NAME}:${IMAGE_TAG} .

# Step 2: Login to ECR
echo "🔐 Logging into ECR..."
aws ecr get-login-password --region ${AWS_REGION} | 
  docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# Step 3: Tag and push image
echo "⬆️ Pushing image to ECR..."
docker tag ${ECR_REPO_NAME}:${IMAGE_TAG} 
  ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}:${IMAGE_TAG}

docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}:${IMAGE_TAG}

# Step 4: Deploy with Terraform
echo "🏗️ Deploying infrastructure with Terraform..."
cd ../terraform
terraform init
terraform apply -auto-approve

# Step 5: Get task IP
echo "📍 Getting task public IP..."
CLUSTER_NAME=$(terraform output -raw ecs_cluster_name)
SERVICE_NAME=$(terraform output -raw ecs_service_name)

# Wait for service to stabilize
echo "⏳ Waiting for service to stabilize..."
aws ecs wait services-stable --cluster ${CLUSTER_NAME} --services ${SERVICE_NAME} --region ${AWS_REGION}

# Get task ARN
TASK_ARN=$(aws ecs list-tasks --cluster ${CLUSTER_NAME} --service-name ${SERVICE_NAME} --region ${AWS_REGION} --query 'taskArns[0]' --output text)

# Get ENI ID
ENI_ID=$(aws ecs describe-tasks --cluster ${CLUSTER_NAME} --tasks ${TASK_ARN} --region ${AWS_REGION} 
  --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' --output text)

# Get public IP
PUBLIC_IP=$(aws ec2 describe-network-interfaces --network-interface-ids ${ENI_ID} --region ${AWS_REGION} 
  --query 'NetworkInterfaces[0].Association.PublicIp' --output text)

echo "✅ Deployment complete!"
echo "🌐 MCP Server URL: http://${PUBLIC_IP}:8000/mcp/"
echo "💚 Health Check: http://${PUBLIC_IP}:8000/health"

make a github workflow instead, I already set the aws access key and secret in the repo secrets
Model: I'll create a GitHub Actions workflow to deploy your MCP server to AWS. This workflow will handle both the initial deployment and updates.

## GitHub Actions Workflow

### `.github/workflows/deploy.yml`
```yaml
name: Deploy MCP Server to AWS

on:
  push:
    branches:
      - main
      - master
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy to'
        required: true
        default: 'production'
        type: choice
        options:
          - production
          - staging
          - development

env:
  AWS_REGION: us-east-1
  ECR_REPO_NAME: mcp-server-repo
  IMAGE_TAG: ${{ github.sha }}

jobs:
  build-and-push:
    name: Build and Push Docker Image
    runs-on: ubuntu-latest
    outputs:
      image-url: ${{ steps.build.outputs.image-url }}
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Check if ECR repository exists
        id: check-ecr
        run: |
          if aws ecr describe-repositories --repository-names ${{ env.ECR_REPO_NAME }} 2>/dev/null; then
            echo "exists=true" >> $GITHUB_OUTPUT
          else
            echo "exists=false" >> $GITHUB_OUTPUT
          fi

      - name: Create ECR repository if it doesn't exist
        if: steps.check-ecr.outputs.exists == 'false'
        run: |
          aws ecr create-repository \
            --repository-name ${{ env.ECR_REPO_NAME }} \
            --image-scanning-configuration scanOnPush=true \
            --region ${{ env.AWS_REGION }}

      - name: Build, tag, and push Docker image
        id: build
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        run: |
          cd app
          docker build -t $ECR_REGISTRY/${{ env.ECR_REPO_NAME }}:${{ env.IMAGE_TAG }} .
          docker tag $ECR_REGISTRY/${{ env.ECR_REPO_NAME }}:${{ env.IMAGE_TAG }} $ECR_REGISTRY/${{ env.ECR_REPO_NAME }}:latest
          docker push $ECR_REGISTRY/${{ env.ECR_REPO_NAME }}:${{ env.IMAGE_TAG }}
          docker push $ECR_REGISTRY/${{ env.ECR_REPO_NAME }}:latest
          echo "image-url=$ECR_REGISTRY/${{ env.ECR_REPO_NAME }}:${{ env.IMAGE_TAG }}" >> $GITHUB_OUTPUT

  deploy-infrastructure:
    name: Deploy Infrastructure with Terraform
    runs-on: ubuntu-latest
    needs: build-and-push
    outputs:
      cluster-name: ${{ steps.outputs.outputs.cluster-name }}
      service-name: ${{ steps.outputs.outputs.service-name }}
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: 1.6.0

      - name: Terraform Init
        working-directory: ./terraform
        run: terraform init

      - name: Terraform Plan
        working-directory: ./terraform
        run: |
          terraform plan \
            -var="aws_region=${{ env.AWS_REGION }}" \
            -var="environment=${{ github.event.inputs.environment || 'production' }}" \
            -out=tfplan

      - name: Terraform Apply
        working-directory: ./terraform
        run: terraform apply -auto-approve tfplan

      - name: Get Terraform Outputs
        id: outputs
        working-directory: ./terraform
        run: |
          echo "cluster-name=$(terraform output -raw ecs_cluster_name)" >> $GITHUB_OUTPUT
          echo "service-name=$(terraform output -raw ecs_service_name)" >> $GITHUB_OUTPUT

  update-service:
    name: Update ECS Service
    runs-on: ubuntu-latest
    needs: [build-and-push, deploy-infrastructure]
    
    steps:
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Force new deployment
        run: |
          aws ecs update-service \
            --cluster ${{ needs.deploy-infrastructure.outputs.cluster-name }} \
            --service ${{ needs.deploy-infrastructure.outputs.service-name }} \
            --force-new-deployment \
            --region ${{ env.AWS_REGION }}

      - name: Wait for service to stabilize
        run: |
          aws ecs wait services-stable \
            --cluster ${{ needs.deploy-infrastructure.outputs.cluster-name }} \
            --services ${{ needs.deploy-infrastructure.outputs.service-name }} \
            --region ${{ env.AWS_REGION }}

  get-deployment-info:
    name: Get Deployment Information
    runs-on: ubuntu-latest
    needs: [deploy-infrastructure, update-service]
    
    steps:
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Get Task Public IP
        id: get-ip
        run: |
          # Get task ARN
          TASK_ARN=$(aws ecs list-tasks \
            --cluster ${{ needs.deploy-infrastructure.outputs.cluster-name }} \
            --service-name ${{ needs.deploy-infrastructure.outputs.service-name }} \
            --region ${{ env.AWS_REGION }} \
            --query 'taskArns[0]' \
            --output text)
          
          if [ "$TASK_ARN" != "None" ] && [ ! -z "$TASK_ARN" ]; then
            # Get ENI ID
            ENI_ID=$(aws ecs describe-tasks \
              --cluster ${{ needs.deploy-infrastructure.outputs.cluster-name }} \
              --tasks $TASK_ARN \
              --region ${{ env.AWS_REGION }} \
              --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' \
              --output text)
            
            if [ "$ENI_ID" != "None" ] && [ ! -z "$ENI_ID" ]; then
              # Get public IP
              PUBLIC_IP=$(aws ec2 describe-network-interfaces \
                --network-interface-ids $ENI_ID \
                --region ${{ env.AWS_REGION }} \
                --query 'NetworkInterfaces[0].Association.PublicIp' \
                --output text)
              
              echo "public-ip=$PUBLIC_IP" >> $GITHUB_OUTPUT
              echo "success=true" >> $GITHUB_OUTPUT
            else
              echo "success=false" >> $GITHUB_OUTPUT
            fi
          else
            echo "success=false" >> $GITHUB_OUTPUT
          fi

      - name: Display Deployment Information
        if: steps.get-ip.outputs.success == 'true'
        run: |
          echo "## 🎉 Deployment Successful!" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "### 🌐 Endpoints" >> $GITHUB_STEP_SUMMARY
          echo "- **MCP Server**: http://${{ steps.get-ip.outputs.public-ip }}:8000/mcp/" >> $GITHUB_STEP_SUMMARY
          echo "- **Health Check**: http://${{ steps.get-ip.outputs.public-ip }}:8000/health" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "### 📦 Deployment Details" >> $GITHUB_STEP_SUMMARY
          echo "- **Environment**: ${{ github.event.inputs.environment || 'production' }}" >> $GITHUB_STEP_SUMMARY
          echo "- **Image Tag**: ${{ env.IMAGE_TAG }}" >> $GITHUB_STEP_SUMMARY
          echo "- **Region**: ${{ env.AWS_REGION }}" >> $GITHUB_STEP_SUMMARY
          echo "- **Cluster**: ${{ needs.deploy-infrastructure.outputs.cluster-name }}" >> $GITHUB_STEP_SUMMARY
          echo "- **Service**: ${{ needs.deploy-infrastructure.outputs.service-name }}" >> $GITHUB_STEP_SUMMARY

      - name: Test Health Endpoint
        if: steps.get-ip.outputs.success == 'true'
        run: |
          echo "Testing health endpoint..."
          max_attempts=10
          attempt=0
          
          while [ $attempt -lt $max_attempts ]; do
            if curl -f http://${{ steps.get-ip.outputs.public-ip }}:8000/health; then
              echo "✅ Health check passed!"
              break
            else
              echo "Attempt $((attempt + 1))/$max_attempts failed. Waiting 10 seconds..."
              sleep 10
              attempt=$((attempt + 1))
            fi
          done
          
          if [ $attempt -eq $max_attempts ]; then
            echo "⚠️ Health check failed after $max_attempts attempts"
            exit 1
          fi
```

### `.github/workflows/destroy.yml`
```yaml
name: Destroy MCP Server Infrastructure

on:
  workflow_dispatch:
    inputs:
      confirm:
        description: 'Type "destroy" to confirm infrastructure destruction'
        required: true
        type: string

env:
  AWS_REGION: us-east-1

jobs:
  destroy:
    name: Destroy Infrastructure
    runs-on: ubuntu-latest
    if: github.event.inputs.confirm == 'destroy'
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: 1.6.0

      - name: Terraform Init
        working-directory: ./terraform
        run: terraform init

      - name: Terraform Destroy
        working-directory: ./terraform
        run: terraform destroy -auto-approve

      - name: Summary
        run: |
          echo "## 🗑️ Infrastructure Destroyed" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "All AWS resources have been successfully destroyed." >> $GITHUB_STEP_SUMMARY
```

### `.github/workflows/validate.yml`
```yaml
name: Validate and Test

on:
  pull_request:
    branches:
      - main
      - master
    paths:
      - 'app/**'
      - 'terraform/**'
      - '.github/workflows/**'

env:
  AWS_REGION: us-east-1

jobs:
  validate-terraform:
    name: Validate Terraform
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: 1.6.0

      - name: Terraform Init
        working-directory: ./terraform
        run: terraform init -backend=false

      - name: Terraform Format Check
        working-directory: ./terraform
        run: terraform fmt -check -recursive

      - name: Terraform Validate
        working-directory: ./terraform
        run: terraform validate

  test-docker-build:
    name: Test Docker Build
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Build Docker image
        working-directory: ./app
        run: docker build -t mcp-server:test .

      - name: Run container test
        run: |
          docker run -d -p 8000:8000 --name mcp-test mcp-server:test
          sleep 10
          curl -f http://localhost:8000/health || exit 1
          docker stop mcp-test
```

## Additional Files

### `.github/dependabot.yml`
```yaml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    
  - package-ecosystem: "pip"
    directory: "/app"
    schedule:
      interval: "weekly"
    
  - package-ecosystem: "terraform"
    directory: "/terraform"
    schedule:
      interval: "weekly"
```

### `terraform/backend.tf`
Add this file to store Terraform state in S3 (recommended for GitHub Actions):

```hcl
terraform {
  backend "s3" {
    bucket = "your-terraform-state-bucket"  # Create this bucket first
    key    = "mcp-server/terraform.tfstate"
    region = "us-east-1"
    # Optional: enable state locking with DynamoDB
    # dynamodb_table = "terraform-state-lock"
  }
}
```

## Setup Instructions

### `README.md` (Updated Section)
```markdown
# GitHub Actions Deployment

## Prerequisites

1. Set up AWS credentials in GitHub Secrets:
   - Go to Settings → Secrets and variables → Actions
   - Add the following secrets:
     - `AWS_ACCESS_KEY_ID`: Your AWS access key
     - `AWS_SECRET_ACCESS_KEY`: Your AWS secret key

2. (Optional) Create S3 bucket for Terraform state:
   ```bash
   aws s3api create-bucket --bucket your-terraform-state-bucket --region us-east-1
   ```

## Deployment

### Automatic Deployment
Push to the `main` branch to trigger automatic deployment:
```bash
git add .
git commit -m "Deploy MCP server"
git push origin main
```

### Manual Deployment
1. Go to Actions tab in GitHub
2. Select "Deploy MCP Server to AWS"
3. Click "Run workflow"
4. Select branch and environment
5. Click "Run workflow" button

## Monitoring Deployment

1. Go to the Actions tab
2. Click on the running workflow
3. View real-time logs for each job
4. Check the Summary for deployment URLs

## Destroying Infrastructure

To destroy all AWS resources:
1. Go to Actions tab
2. Select "Destroy MCP Server Infrastructure"
3. Click "Run workflow"
4. Type "destroy" to confirm
5. Click "Run workflow" button

## Pull Request Validation

All pull requests will automatically:
- Validate Terraform configuration
- Test Docker build
- Check code formatting

## Deployment Outputs

After successful deployment, check the workflow summary for:
- MCP Server URL
- Health check endpoint
- Task public IP
- Deployment details
```

This GitHub Actions workflow provides:

1. **Automated deployment** on push to main branch
2. **Manual deployment** with environment selection
3. **Docker image building** and pushing to ECR
4. **Terraform infrastructure** deployment
5. **ECS service updates** with new images
6. **Deployment information** in workflow summary
7. **Health check validation** after deployment
8. **Pull request validation** for code changes
9. **Infrastructure destruction** workflow with confirmation
10. **Dependabot** for keeping dependencies updated

The workflow is modular, with separate jobs for building, deploying, and updating, making it easy to debug and maintain.