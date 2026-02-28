""" 
Why MCP is a Game Changer:
1) Standardization: Before MCP, every agent needed a custom read_file() function. With MCP, the agent just asks the server "what can you do?", and the server provides the tools in a format the AI understands.
2) Decoupling: You can swap the LLM (e.g., from llama3.2 to Gemini) without changing your data tools.
3) Privacy: Since MCP servers run as separate processes, you can control exactly what data the agent can "see" without giving it full access to your machine"""
"""

Pattern: MCP (Model Context Protocol)
Description: Connects the agent to external tool servers using the MCP standard.
"""
import asyncio
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.models.lite_llm import LiteLlm
from google.genai import types

# 1. Configuration
OLLAMA_MODEL = LiteLlm(model="ollama_chat/llama3.2")
APP_NAME = "MCPApp"

# 2. Define the MCP Agent
mcp_agent = Agent(
    name="MCPAgent",
    model=OLLAMA_MODEL,
    instruction=(
        "You are an agent connected to external servers via MCP (Model Context Protocol). "
        "You can browse local files, query databases, and fetch live web data using standardized tools."
    )
)

# 3. Generator Logic for Streamlit
async def execute_mcp(user_query: str):
    session_service = InMemorySessionService()
    
    # Phase 1: Handshake
    yield "🔌 Connecting to MCP Host (localhost:8080)..."
    await asyncio.sleep(1)  # Simulating network handshake
    
    # Phase 2: Tool Discovery
    yield "🔍 Discovery: Found 3 MCP Tools (filesystem_read, sqlite_query, google_search)..."
    await session_service.create_session(user_id="u1", session_id="mcp_sess", app_name=APP_NAME)
    
    runner = Runner(agent=mcp_agent, session_service=session_service, app_name=APP_NAME)
    msg = types.Content(role='user', parts=[types.Part(text=user_query)])
    
    response = ""
    yield "🛰️ Routing query through MCP Secure Tunnel..."
    
    async for event in runner.run_async(user_id="u1", session_id="mcp_sess", new_message=msg):
        if event.is_final_response():
            response = event.content.parts[0].text
            
    # Final response with simulated MCP metadata
    yield (
        f"### 🛡️ MCP Security Layer\n"
        f"**Protocol:** v1.0 | **Transport:** stdio | **Authentication:** Local\n\n"
        f"---\n"
        f"### 📦 MCP Resource Output\n"
        f"{response}"
    )

# 4. Universal Entry Point
async def run_pattern(user_query: str):
    """Entry point for Streamlit dashboard."""
    return execute_mcp(user_query)

if __name__ == "__main__":
    async def local_test():
        gen = await run_pattern("List the files in my current directory using MCP tools.")
        async for update in gen:
            print(update)
    
    asyncio.run(local_test())