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
