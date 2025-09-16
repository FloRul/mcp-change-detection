import os
from fastmcp import FastMCP
from fastmcp.server.auth.providers.azure import AzureProvider

import boto3

SECRETS_NAME = os.environ.get("SECRET_NAME", "azure_credentials")
REGION = os.environ.get("AWS_REGION", "ca-central-1")


def get_azure_credentials():
    client = boto3.client("secretsmanager", region_name=REGION)
    response = client.get_secret_value(SecretId=SECRETS_NAME)
    secret = response["SecretString"]
    return eval(secret)


credentials = get_azure_credentials()

auth_provider = AzureProvider(
    client_id=credentials["client_id"],
    client_secret=credentials["client_secret"],
    tenant_id=credentials["tenant_id"],
    required_scopes=[
        "User.Read",
        "email",
        "openid",
        "profile",
    ],  # Default value, customize if needed
)

# Read configuration from environment
server_name = os.environ.get("MCP_SERVER_NAME", "Remote MCP Server")

mcp = FastMCP(name=server_name, auth=auth_provider)


@mcp.tool
async def get_user_info() -> dict:
    """Returns information about the authenticated Azure user."""
    from fastmcp.server.dependencies import get_access_token

    token = get_access_token()
    # The AzureProvider stores user data in token claims
    return {
        "azure_id": token.claims.get("sub"),
        "email": token.claims.get("email"),
        "name": token.claims.get("name"),
        "job_title": token.claims.get("job_title"),
        "office_location": token.claims.get("office_location"),
    }


# Example tools
@mcp.tool
def process_data(input: str) -> str:
    """Process data on the server"""
    return f"Processed: {input}"


@mcp.tool
def get_server_info() -> dict:
    """Get information about the server"""
    return {"name": server_name, "version": "1.0.0", "status": "running"}


# Health check endpoint
from starlette.responses import JSONResponse


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    return JSONResponse({"status": "healthy", "service": "mcp-server"})


app = mcp.http_app(transport="streamable-http", stateless_http=True)
