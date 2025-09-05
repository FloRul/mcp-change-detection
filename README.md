# FastMCP Server AWS Deployment

A production-ready Terraform configuration for deploying a FastMCP server on AWS using ECS Fargate, with auto-scaling, monitoring, and security best practices.

## 🚀 Features

- **Serverless Container Deployment** - Uses AWS ECS Fargate for zero-maintenance infrastructure
- **High Availability** - Multi-AZ deployment with Application Load Balancer
- **Auto-scaling** - Automatically scales based on CPU and memory utilization
- **Security First** - VPC isolation, security groups, and secrets management
- **HTTPS Support** - Optional SSL/TLS termination with ACM certificates
- **Custom Domain** - Route53 integration for custom domain names
- **Monitoring** - CloudWatch logs, metrics, and alarms
- **CI/CD Ready** - GitHub Actions workflow for automated deployments
- **Cost Optimized** - Efficient resource allocation with Fargate

## 📋 Prerequisites

### Required Tools

- [Terraform](https://www.terraform.io/downloads)
- [AWS CLI](https://aws.amazon.com/cli/)
- [Docker](https://www.docker.com/get-started)
- An AWS account with appropriate permissions

### AWS Permissions

Your AWS credentials need permissions for:
- VPC and networking resources
- ECS (Cluster, Services, Task Definitions)
- ECR (Container Registry)
- IAM roles and policies
- Application Load Balancer
- CloudWatch logs and metrics
- Secrets Manager
- (Optional) Route53 and ACM for custom domains

## 🏗️ Architecture

```mermaid
graph TB
    subgraph Internet
        Users[Users/Clients]
    end
    
    subgraph AWS Cloud
        subgraph VPC
            ALB[Application Load Balancer]
            
            subgraph Public Subnets
                NAT1[NAT Gateway 1]
                NAT2[NAT Gateway 2]
            end
            
            subgraph Private Subnets
                ECS1[ECS Task 1]
                ECS2[ECS Task 2]
                ECS3[ECS Task N...]
            end
        end
        
        ECR[ECR Repository]
        SM[Secrets Manager]
        CW[CloudWatch]
        R53[Route53]
        ACM[ACM Certificate]
    end
    
    Users --> ALB
    ALB --> ECS1
    ALB --> ECS2
    ALB --> ECS3
    ECS1 --> ECR
    ECS1 --> SM
    ECS1 --> CW
    R53 --> ALB
    ACM --> ALB
```

## 📁 Project Structure

```
fastmcp-aws-deployment/
├── terraform/
│   ├── main.tf                 # Main Terraform configuration
│   ├── variables.tf            # Variable definitions
│   ├── outputs.tf              # Output definitions
│   └── terraform.tfvars.example # Example variables file
├── mcp/
│   ├── server.py               # FastMCP server implementation
│   ├── requirements.txt        # Python dependencies
│   └── Dockerfile              # Container image definition
├── .github/
│   └── workflows/
│       └── deploy.yml          # GitHub Actions deployment
└── README.md                   # This file
```

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/fastmcp-aws-deployment.git
cd fastmcp-aws-deployment
```

### 2. Configure Variables

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` with your configuration:

```hcl
aws_region     = "us-east-1"
project_name   = "fastmcp-server"
environment    = "prod"
container_port = 8000
cpu           = "512"
memory        = "1024"
desired_count = 2
min_capacity  = 1
max_capacity  = 10
```

### 3. Set Authentication Token

```bash
export TF_VAR_mcp_auth_token="your-secure-token-here"
```

### 4. Deploy Infrastructure

```bash
# Initialize Terraform
terraform init

# Review the deployment plan
terraform plan

# Deploy the infrastructure
terraform apply -auto-approve
```

### 5. Build and Deploy Application

```bash
# Get ECR repository URL
ECR_URL=$(terraform output -raw ecr_repository_url)

# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin $ECR_URL

# Build and push Docker image
cd ../app
docker build -t $ECR_URL:latest .
docker push $ECR_URL:latest

# Update ECS service
aws ecs update-service \
  --cluster $(terraform -chdir=../terraform output -raw ecs_cluster_name) \
  --service $(terraform -chdir=../terraform output -raw ecs_service_name) \
  --force-new-deployment
```

### 6. Verify Deployment

```bash
# Get the MCP endpoint
MCP_ENDPOINT=$(terraform output -raw mcp_endpoint)
echo "MCP Server: $MCP_ENDPOINT"

# Test health check
curl $(terraform output -raw health_check_endpoint)

# Test MCP endpoint with authentication
curl -H "Authorization: Bearer your-secure-token-here" $MCP_ENDPOINT
```

## 🔧 Configuration

### Environment Variables

The FastMCP server supports the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_AUTH_TOKEN` | Bearer token for authentication | None (no auth) |
| `MCP_PATH` | Path for MCP endpoint | `/mcp/` |
| `PORT` | Server port | `8000` |
| `ENVIRONMENT` | Environment name | `unknown` |

### Terraform Variables

Key configuration options in `terraform.tfvars`:

| Variable | Description | Default |
|----------|-------------|---------|
| `aws_region` | AWS region for deployment | `us-east-1` |
| `project_name` | Project name for resource naming | `fastmcp-server` |
| `environment` | Environment (dev/staging/prod) | `prod` |
| `container_port` | Container port | `8000` |
| `cpu` | Fargate CPU units | `512` |
| `memory` | Fargate memory (MB) | `1024` |
| `desired_count` | Number of tasks | `2` |
| `min_capacity` | Minimum tasks for auto-scaling | `1` |
| `max_capacity` | Maximum tasks for auto-scaling | `10` |
| `certificate_arn` | ACM certificate ARN for HTTPS | None |
| `domain_name` | Custom domain name | None |
| `route53_zone_id` | Route53 hosted zone ID | None |

## 🔒 Security

### Authentication

FastMCP supports multiple authentication methods. This deployment uses Bearer token authentication:

```python
# In server.py
auth = BearerTokenAuth(token=auth_token)
mcp = FastMCP("Production MCP Server", auth=auth)
```

For production, consider using OAuth 2.0 authentication instead.

### Network Security

- **VPC Isolation**: All resources run in a dedicated VPC
- **Private Subnets**: ECS tasks run in private subnets
- **Security Groups**: Restrictive inbound rules, only ALB can reach tasks
- **Secrets Management**: Authentication tokens stored in AWS Secrets Manager

### HTTPS Configuration

To enable HTTPS:

1. Request an ACM certificate:
```bash
aws acm request-certificate \
  --domain-name mcp.example.com \
  --validation-method DNS
```

2. Add to `terraform.tfvars`:
```hcl
certificate_arn = "arn:aws:acm:us-east-1:123456789012:certificate/..."
domain_name     = "mcp.example.com"
route53_zone_id = "Z1234567890ABC"
```

3. Apply changes:
```bash
terraform apply
```

## 📊 Monitoring

### CloudWatch Logs

View application logs:

```bash
# Stream logs in real-time
aws logs tail /ecs/fastmcp-server-prod --follow

# Query recent logs
aws logs filter-log-events \
  --log-group-name /ecs/fastmcp-server-prod \
  --start-time $(date -u -d '5 minutes ago' +%s)000
```

### Metrics and Alarms

The deployment includes CloudWatch alarms for:
- High CPU utilization (>80%)
- High memory utilization (>80%)

View metrics:

```bash
# Get CPU metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=fastmcp-server-prod \
               Name=ClusterName,Value=fastmcp-server-prod \
  --start-time $(date -u -d '1 hour ago' --iso-8601) \
  --end-time $(date -u --iso-8601) \
  --period 300 \
  --statistics Average
```

### Custom Dashboards

Create a CloudWatch dashboard for your MCP server:

```bash
aws cloudwatch put-dashboard \
  --dashboard-name fastmcp-server \
  --dashboard-body file://dashboard.json
```

## 🔄 CI/CD

### GitHub Actions

The included workflow automatically deploys on push to main:

1. Set up GitHub secrets:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`

2. Push to main branch:
```bash
git add .
git commit -m "Update MCP server"
git push origin main
```

3. Monitor deployment:
   - Check GitHub Actions tab
   - View ECS service updates in AWS console

### Manual Deployment

Update the application without Terraform:

```bash
# Build and push new image
docker build -t $ECR_URL:latest app/
docker push $ECR_URL:latest

# Force new deployment
aws ecs update-service \
  --cluster fastmcp-server-prod \
  --service fastmcp-server-prod \
  --force-new-deployment
```

## 📈 Scaling

### Auto-scaling Configuration

The service automatically scales based on:
- CPU utilization (target: 70%)
- Memory utilization (target: 70%)

### Manual Scaling

Temporarily adjust capacity:

```bash
# Scale up
aws ecs update-service \
  --cluster fastmcp-server-prod \
  --service fastmcp-server-prod \
  --desired-count 5

# Scale down
aws ecs update-service \
  --cluster fastmcp-server-prod \
  --service fastmcp-server-prod \
  --desired-count 1
```

### Permanent Scaling Changes

Update `terraform.tfvars`:

```hcl
min_capacity = 2
max_capacity = 20
```

Apply changes:

```bash
terraform apply
```

## 💰 Cost Management

### Estimated Costs

Monthly costs (us-east-1, 2 tasks running 24/7):

| Service | Configuration | Estimated Cost |
|---------|--------------|----------------|
| ECS Fargate | 2 × (0.5 vCPU, 1GB) | ~$36 |
| Application Load Balancer | 1 ALB | ~$25 |
| CloudWatch Logs | 10GB/month | ~$5 |
| Secrets Manager | 1 secret | ~$0.40 |
| Data Transfer | 100GB/month | ~$9 |
| **Total** | | **~$75/month** |

### Cost Optimization Tips

1. **Use Fargate Spot** for non-critical workloads (up to 70% savings)
2. **Implement request caching** to reduce backend calls
3. **Adjust auto-scaling thresholds** based on actual usage
4. **Use AWS Savings Plans** for predictable workloads
5. **Clean up unused resources** regularly

## 🧪 Testing

### Local Testing

Test your FastMCP server locally before deployment:

```bash
cd app
pip install -r requirements.txt
python server.py
```

Test endpoints:

```bash
# Health check
curl http://localhost:8000/health

# MCP endpoint
curl -H "Authorization: Bearer test-token" \
  http://localhost:8000/mcp/
```

### Integration Testing

After deployment:

```bash
# Set variables
MCP_URL=$(terraform output -raw mcp_endpoint)
AUTH_TOKEN="your-secure-token-here"

# Test MCP tool
curl -X POST $MCP_URL \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "process_data",
      "arguments": {"input": "test data"}
    }
  }'
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. ECS Tasks Not Starting

Check task logs:
```bash
aws ecs describe-tasks \
  --cluster fastmcp-server-prod \
  --tasks $(aws ecs list-tasks --cluster fastmcp-server-prod --query 'taskArns[0]' --output text)
```

#### 2. Health Checks Failing

Verify security groups allow ALB to reach tasks:
```bash
aws ec2 describe-security-groups \
  --filters "Name=tag:Name,Values=*ecs-tasks*"
```

#### 3. Cannot Access MCP Endpoint

Check ALB target health:
```bash
aws elbv2 describe-target-health \
  --target-group-arn $(aws elbv2 describe-target-groups \
    --names "mcp-*" --query 'TargetGroups[0].TargetGroupArn' --output text)
```

#### 4. Authentication Errors

Verify secret is accessible:
```bash
aws secretsmanager get-secret-value \
  --secret-id fastmcp-server-prod-mcp-auth
```

### Debug Mode

Enable detailed logging:

```python
# In server.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🧹 Cleanup

Remove all resources when no longer needed:

```bash
# Destroy infrastructure
cd terraform
terraform destroy -auto-approve

# Verify all resources removed
aws ecs list-clusters --query 'clusterArns[?contains(@, `fastmcp`)]'
aws ec2 describe-vpcs --filters "Name=tag:Project,Values=fastmcp-server"
```

## 📚 Additional Resources

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [MCP Specification](https://modelcontextprotocol.io/)
- [AWS ECS Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastMCP](https://github.com/jlowin/fastmcp) for the excellent MCP framework
- [Anthropic](https://www.anthropic.com/) for the Model Context Protocol
- AWS for the robust cloud infrastructure

## 📧 Support

For issues and questions:
- Open an issue in this repository
- Check existing issues for solutions
- Review the FastMCP documentation

---

**Happy Deploying! 🚀**