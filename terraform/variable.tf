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
  nullable    = false
}

variable "availability_zone" {
  description = "Availability zone for the subnet"
  type        = string
  default     = "ca-central-1a"
}
