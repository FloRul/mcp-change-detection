resource "aws_secretsmanager_secret" "azure_credentials" {
  name = "azure_credentials"
  description = "Azure credentials for MCP"
}