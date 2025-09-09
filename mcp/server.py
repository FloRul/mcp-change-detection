import os
from fastmcp import FastMCP
from fastmcp.server.auth.providers.azure import AzureProvider

auth_provider = AzureProvider(
    
    required_scopes=[
        "User.Read",
        "email",
        "openid",
        "profile",
    ],  # Microsoft Graph permissions
    # redirect_path="/auth/callback"                  # Default value, customize if needed
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


app = mcp.http_app(transport="streamable-http")
