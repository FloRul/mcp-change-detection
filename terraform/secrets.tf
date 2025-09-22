resource "aws_secretsmanager_secret" "mcp_secret" {
  name        = "mcp_secret"
  description = "MCP secrets for ${var.project_name} in ${var.environment}"
}
