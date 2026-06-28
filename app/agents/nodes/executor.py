import structlog
import json
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from app.llm.router import get_llm_router
from app.llm.prompts import EXECUTOR_SYSTEM_PROMPT
from app.agents.state import AgentState
from app.tools.mcp_manager import MCPManager
from app.tools.implementations.code_interpreter import CodeInterpreterTool
from app.tools.implementations.web_scraper import WebScraperTool

logger = structlog.get_logger(__name__)

async def execute_node(state: AgentState) -> Dict[str, Any]:
    """Executes the current step using LLM function calling and internal/MCP tools."""
    logger.info("node_execute_start", step=state["current_step"])
    
    if state["current_step"] >= len(state["plan"]):
        return {"is_complete": True}
        
    current_plan_step = state["plan"][state["current_step"]]
    router = get_llm_router()
    
    # Initialize Internal Tools
    internal_tools_map = {
        "code_interpreter": CodeInterpreterTool(),
        "web_scraper": WebScraperTool()
    }
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "code_interpreter",
                "description": "Executes Python code in an isolated directory.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "Python code to execute"}
                    },
                    "required": ["code"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "web_scraper",
                "description": "Fetches and parses text content from a given URL.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "The URL to scrape"}
                    },
                    "required": ["url"]
                }
            }
        }
    ]
    
    mcp_manager = MCPManager()
    # In a full deployment, these could be pulled from env vars or config
    # For now, if we are in Docker, we connect to the local containers via their CLI entrypoints
    # For local execution, ensure mcp-server-sqlite and mcp-server-filesystem are installed
    try:
        await mcp_manager.connect_server("npx", ["-y", "@modelcontextprotocol/server-sqlite", "--db-path", "/tmp/test.db"])
        mcp_tools = await mcp_manager.list_all_tools()
        for t in mcp_tools:
            tools.append({
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.inputSchema
                }
            })
    except Exception as e:
        logger.warning("mcp_connection_skipped", error=str(e))
    
    messages_payload = [
        {"role": "system", "content": EXECUTOR_SYSTEM_PROMPT},
        {"role": "user", "content": f"Execute the following task: {current_plan_step['description']}"}
    ]
    
    for msg in state["messages"][-5:]:
        if isinstance(msg, AIMessage) or isinstance(msg, HumanMessage):
            messages_payload.append({"role": msg.type, "content": msg.content})
    
    try:
        response = await router.acompletion(
            model_type="coding", 
            messages=messages_payload,
            tools=tools,
            tool_choice="auto"
        )
        
        message = response.choices[0].message
        new_messages = [AIMessage(content=message.content or "")]
        
        if hasattr(message, "tool_calls") and message.tool_calls:
            for tc in message.tool_calls:
                func_name = tc.function.name
                args = json.loads(tc.function.arguments)
                
                logger.info("tool_call", tool=func_name, args=args)
                
                try:
                    if func_name in internal_tools_map:
                        result = await internal_tools_map[func_name].execute(**args)
                    else:
                        result = await mcp_manager.execute_tool(func_name, args)
                except Exception as tool_e:
                    result = f"Error executing tool {func_name}: {str(tool_e)}"
                    
                new_messages.append(ToolMessage(content=str(result), tool_call_id=tc.id))
                
        await mcp_manager.cleanup()
        return {"messages": new_messages}
        
    except Exception as e:
        logger.error("node_execute_error", error=str(e))
        await mcp_manager.cleanup()
        return {"messages": [AIMessage(content=f"Execution failed: {str(e)}")]}
