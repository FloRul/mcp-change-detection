output "load_balancer_url" {
  description = "URL of the load balancer"
  value       = "http://\${aws_lb.main.dns_name}"
}

output "mcp_endpoint" {
  description = "MCP server endpoint"
  value       = "http://\${aws_lb.main.dns_name}\${var.mcp_path}"
}

output "health_check_endpoint" {
  description = "Health check endpoint"
  value       = "http://\${aws_lb.main.dns_name}\${var.health_check_path}"
}

output "ecr_repository_url" {
  description = "ECR repository URL"
  value       = aws_ecr_repository.main.repository_url
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  description = "ECS service name"
  value       = aws_ecs_service.main.name
}

output "cloudwatch_log_group" {
  description = "CloudWatch log group name"
  value       = aws_cloudwatch_log_group.main.name
}

output "custom_domain_url" {
  description = "Custom domain URL (if configured)"
  value       = var.domain_name != "" ? "https://\${var.domain_name}" : "Not configured"
}