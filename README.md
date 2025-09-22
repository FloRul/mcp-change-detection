# MCP Change Detection — Terraform infrastructure

This repository contains Terraform configuration to provision AWS infrastructure for the MCP (fastmcp-server) service. It creates a VPC, public subnet, ECS cluster, task definition, service, CloudWatch Log Group, IAM roles, and Secrets Manager secret. There's also a GitHub Actions workflow that builds and pushes the Docker image to ECR and runs Terraform to apply the infrastructure.

## What this repo contains

- `terraform/` — Terraform configuration and variables
  - `provider.tf` — AWS provider configuration and S3 backend
  - `vpc.tf` — VPC, subnet, route table, IGW, and security group
  - `ecr.tf` — ECS cluster, task definition, service, CloudWatch logs, and IAM roles
  - `secrets.tf` — Secrets Manager secret resource
  - `variable.tf` — Terraform input variables
  - `var.tfvars` — Example values used for local testing
- `mcp/` — Application Dockerfile and server code (image built and pushed by CI)
- `.github/workflows/deploy.yml` — CI workflow to build/push image and apply Terraform

## High-level architecture

1. ECR repository stores the Docker image for the MCP server.
2. ECS Fargate runs the task using the pushed image.
3. Tasks are placed in a public subnet and are reachable via their public IP (the service uses assign_public_ip = true).
4. Secrets required by the container are stored in AWS Secrets Manager and granted read permission via an IAM task role policy.
5. Logs are sent to CloudWatch Logs under `/ecs/${var.project_name}`.

## Prerequisites

- An AWS account and IAM credentials with permission to create VPCs, ECS, ECR, IAM roles/policies, CloudWatch, and Secrets Manager.
- Terraform 1.3+ (the workflow uses 1.13.1; use a compatible version)
- AWS CLI (optional, for inspecting outputs and debugging)
- Docker (to build images locally if desired)

## Backend

This configuration uses an S3 backend defined in `provider.tf`:

- bucket: `levio-mcp-terraform-backend-2`
- key: `terraform/terraform.tfstate`
- region: `ca-central-1`

If you want to use a different backend or local state for testing, update `provider.tf` accordingly.

## Input variables

Key variables (defined in `variable.tf`):

- `aws_region` — AWS region for deployment (default `us-east-1`)
- `project_name` — Project name used for resource naming (default `mcp-server`)
- `environment` — Environment name (default `production`)
- `container_port` — Port the container listens on (default `8000`)
- `task_cpu` / `task_memory` — Fargate CPU/memory
- `desired_count` — Number of tasks to run
- `mcp_server_name` — ECR repository / image name (required)
- `mcp_auth_token` — Sensitive token (sensitive variable)

There is an example `var.tfvars` included for local testing. Update or create your own `terraform.tfvars` file for production values.

## Deploying locally with Terraform

1. Initialize Terraform (from the repo root):

```powershell
cd terraform
terraform init
```

2. Create a plan (pass required vars; `mcp_server_name` must be provided):

```powershell
terraform plan -var="mcp_server_name=<your-ecr-repo-name>" -out=tfplan
```

3. Apply the plan:

```powershell
terraform apply -auto-approve tfplan
```

4. Get outputs:

```powershell
terraform output
```

Notes:
- The `mcp_server_url` and `health_check_url` outputs include a placeholder `<TASK_PUBLIC_IP>` because task public IPs are dynamic. Use the ECS console or the outputs from your deployment pipeline to find the current IP.

## CI/CD (GitHub Actions)

The repository includes a workflow `.github/workflows/deploy.yml` that:

- Builds the Docker image in `mcp/` and pushes it to ECR
- Runs `terraform init`, `terraform plan`, and `terraform apply` in the `terraform/` directory
- Forces a new deployment of the ECS service to pick up the new image
- Attempts to fetch the running task's public IP and hits the `/health` endpoint to verify deployment

Secrets required in the GitHub repository (set in Settings → Secrets):

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

Environment variables used by the workflow (can be changed in the workflow):

- `AWS_REGION` — region used by the workflow (workflow sets `ca-central-1` by default)
- `ECR_REPO_NAME` — name used to create/push the ECR image (workflow default `mcp-server-repo`)

Important: the workflow contains inline shell code that assumes a Linux runner and `bash`/`sh`. It runs `terraform` from the `terraform/` directory and expects `mcp_server_name` to match the ECR repository name.

## Secrets and security

- The Terraform config creates a Secrets Manager secret `mcp_secret` in `secrets.tf`. You should populate the secret value via the AWS Console, CLI or additional Terraform resources (e.g., `aws_secretsmanager_secret_version`) rather than committing secrets in the repository.
- `mcp_auth_token` is declared as a sensitive variable. Do not store sensitive tokens in source control. Use `terraform.tfvars` locally (gitignored) or pass via CI secret injection.

## Outputs

Key Terraform outputs are defined in `terraform/outputs.tf`:

- `ecr_repository_url` — ECR repository URL
- `ecs_cluster_name` — ECS cluster name
- `ecs_service_name` — ECS service name
- `vpc_id`, `public_subnet_id` — network resources
- `mcp_server_url`, `health_check_url` — endpoint templates (replace `<TASK_PUBLIC_IP>` with the actual task IP)

## Common tasks and troubleshooting

- To inspect the running task public IP from the CLI:

```powershell
# Get task ARNs
aws ecs list-tasks --cluster <cluster-name>

# Describe tasks and extract ENI or public IP (may require jq)
aws ecs describe-tasks --cluster <cluster-name> --tasks <task-arn>
```

- If the ECS tasks cannot pull the image, ensure the ECR repository exists, images have been pushed, and the task execution role has correct permissions.
- If health checks fail, check the container logs in CloudWatch under `/ecs/${var.project_name}`.

## License

This project is provided under no specific license. Add a LICENSE file if you intend to open source it.
