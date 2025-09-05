import os
from fastmcp import FastMCP

# Read configuration from environment
server_name = os.environ.get("MCP_SERVER_NAME", "Remote MCP Server")

mcp = FastMCP(server_name)


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


# Create ASGI application for production deployment
app = mcp.http_app(transport="streamable-http")
