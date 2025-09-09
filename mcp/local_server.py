import os
from fastmcp import FastMCP
from fastmcp.server.auth.providers.azure import AzureProvider

# Read configuration from environment
SERVER_NAME = "Local test"
mcp = FastMCP(name=SERVER_NAME)


# Example tools
@mcp.tool
def process_data(input: str) -> str:
    """Process data on the server"""
    return f"Processed: {input}"


@mcp.tool
def get_server_info() -> dict:
    """Get information about the server"""
    return {"name": SERVER_NAME, "version": "1.0.0", "status": "running"}


# Health check endpoint
from starlette.responses import JSONResponse


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    return JSONResponse({"status": "healthy", "service": "mcp-server"})


if __name__ == "__main__":
    mcp.run(transport="stdio")
