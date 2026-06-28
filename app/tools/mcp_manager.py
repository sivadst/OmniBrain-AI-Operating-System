import structlog
import asyncio
from typing import List, Any
# Using stdio transport as requested
from mcp.client.stdio import stdio_client
from mcp.client.session import ClientSession
from mcp import StdioServerParameters

logger = structlog.get_logger(__name__)

class MCPManager:
    def __init__(self):
        self.sessions: List[ClientSession] = []
        self._contexts = []

    async def connect_server(self, command: str, args: List[str]):
        """Connects to a local MCP server via STDIO."""
        logger.info("mcp_connecting", command=command)
        server_params = StdioServerParameters(
            command=command,
            args=args,
            env=None
        )
        
        # Keep references to the transport context and session
        try:
            # Note: The mcp python library is typically used with async context managers.
            # In a long-running service we might need to manage these carefully.
            transport_ctx = stdio_client(server_params)
            read_stream, write_stream = await transport_ctx.__aenter__()
            self._contexts.append(transport_ctx)
            
            session = ClientSession(read_stream, write_stream)
            await session.__aenter__()
            await session.initialize()
            
            self.sessions.append(session)
            logger.info("mcp_connected", command=command)
        except Exception as e:
            logger.error("mcp_connection_failed", command=command, error=str(e))

    async def list_all_tools(self) -> List[Any]:
        """Aggregate tools from all connected MCP servers."""
        all_tools = []
        for session in self.sessions:
            try:
                response = await session.list_tools()
                if hasattr(response, 'tools'):
                    all_tools.extend(response.tools)
            except Exception as e:
                logger.error("mcp_list_tools_error", error=str(e))
        return all_tools

    async def execute_tool(self, tool_name: str, arguments: dict) -> Any:
        """Executes a tool by finding which session owns it."""
        for session in self.sessions:
            try:
                # Find if this session has the tool
                tools_response = await session.list_tools()
                tool_names = [t.name for t in tools_response.tools]
                if tool_name in tool_names:
                    result = await session.call_tool(tool_name, arguments=arguments)
                    return result
            except Exception as e:
                logger.error("mcp_execute_tool_error", tool=tool_name, error=str(e))
        
        raise ValueError(f"Tool {tool_name} not found in any connected MCP server.")

    async def cleanup(self):
        """Close all MCP connections."""
        for session in self.sessions:
            await session.__aexit__(None, None, None)
        for ctx in self._contexts:
            await ctx.__aexit__(None, None, None)
