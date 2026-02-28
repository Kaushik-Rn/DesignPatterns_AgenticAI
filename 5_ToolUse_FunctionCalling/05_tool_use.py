"""
Pattern: Tool Use (Function Calling)
Description: Equips an agent with Python functions to perform real-world tasks.
"""
import asyncio
import datetime
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.models.lite_llm import LiteLlm
from google.genai import types

# 1. Configuration
OLLAMA_MODEL = LiteLlm(model="ollama_chat/llama3.2")
APP_NAME = "ToolUseApp"

# 2. Define your Python "Tools"
def get_system_time() -> str:
    """Returns the current date and time of the system. 
    Use this whenever the user asks for the current time."""
    now = datetime.datetime.now()
    return f"The current system time is {now.strftime('%Y-%m-%d %H:%M:%S')}"

def calculate_investment_growth(principal: float, rate: float, years: int) -> str:
    """
    Calculates compound interest. 
    Args:
        principal: Initial amount of money.
        rate: Annual interest rate as a decimal (e.g., 0.10 for 10%).
        years: Number of years to invest.
    """
    # Force casting to handle LLM string inputs
    p, r, y = float(principal), float(rate), int(years)
    amount = principal * (1 + rate) ** years
    return f"After {years} years, your investment will grow to ${amount:,.2f}"

# 3. Define the Agent and bind the tools
specialist_agent = Agent(
    name="SystemSpecialist",
    model=OLLAMA_MODEL,
    instruction=(
        "You are a helpful assistant with access to specific system tools. "
        "If a user asks for the time or a financial calculation, use your tools. "
        "Do not guess information; always call the relevant tool."
    ),
    tools=[get_system_time, calculate_investment_growth]
)

# 4. Generator Logic for Streamlit
async def execute_tool_use(user_query: str):
    session_service = InMemorySessionService()
    
    yield "🧠 Analyzing query to determine tool requirements..."
    
    await session_service.create_session(
        user_id="u1", 
        session_id="tool_sess", 
        app_name=APP_NAME
    )
    
    runner = Runner(agent=specialist_agent, session_service=session_service, app_name=APP_NAME)
    msg = types.Content(role='user', parts=[types.Part(text=user_query)])
    
    final_response = ""
    
    # The runner.run_async handles the multi-step tool loop
    async for event in runner.run_async(user_id="u1", session_id="tool_sess", new_message=msg):
        
        # Check if the model decided to call a tool
        if hasattr(event, 'content') and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, 'tool_call'):
                    yield f"🛠️ **Tool Call Detected:** Invoking `{part.tool_call.function_name}`..."

        if event.is_final_response():
            final_response = event.content.parts[0].text
            
    yield final_response

# 5. Universal Entry Point
async def run_pattern(user_query: str):
    """Entry point for Streamlit dashboard."""
    return execute_tool_use(user_query)

if __name__ == "__main__":
    async def local_test():
        gen = await run_pattern("Calculate 5000 at 10% for 5 years.")
        async for update in gen:
            print(f"[Update]: {update}")
    
    asyncio.run(local_test())