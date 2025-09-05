import os
from fastmcp import FastMCP
from fastmcp.server.auth import BearerTokenAuth
from starlette.responses import JSONResponse

# Initialize FastMCP with authentication if token is provided
auth_token = os.environ.get("MCP_AUTH_TOKEN")
mcp_path = os.environ.get("MCP_PATH", "/mcp/")

if auth_token:
    auth = BearerTokenAuth(token=auth_token)
    mcp = FastMCP("Production MCP Server", auth=auth)
else:
    mcp = FastMCP("Production MCP Server")


# Add health check endpoint
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    return JSONResponse(
        {
            "status": "healthy",
            "service": "fastmcp-server",
            "version": "1.0.0",
            "environment": os.environ.get("ENVIRONMENT", "unknown"),
        }
    )


# Add your MCP tools
@mcp.tool
def process_data(input: str) -> str:
    """Process data on the server"""
    return f"Processed: {input}"


@mcp.tool
def analyze_text(text: str, mode: str = "summary") -> dict:
    """Analyze text with different modes"""
    return {
        "text": text,
        "mode": mode,
        "word_count": len(text.split()),
        "character_count": len(text),
    }


# Create ASGI app for production deployment
app = mcp.http_app(path=mcp_path)

# For local testing
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    mcp.run(transport="http", host="0.0.0.0", port=port)
