from fastmcp import Client
import asyncio
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp.client.transports import StdioTransport

transport = StreamableHttpTransport(url="http://3.96.207.174:8000/mcp")
client = Client(transport)


async def main():
    # The client will automatically handle Azure OAuth
    # async with Client("http://3.96.207.174:8000/mcp/", auth="oauth") as client:
    async with client:
        # First-time connection will open Azure login in your browser
        # print("✓ Authenticated with Azure!")

        print(f"Connected: {client.is_connected()}")

        # Make multiple calls within the same session
        tools = await client.list_tools()
        for tool in tools:
            print(tool)

        # # Test the protected tool
        # result = await client.call_tool("get_user_info")
        # print(f"Azure user: {result['email']}")
        # print(f"Name: {result['name']}")


if __name__ == "__main__":
    asyncio.run(main())
