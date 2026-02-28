"""
Pattern: Planning (Goal Decomposition)
Description: Agent creates a structured plan before executing a complex task.
"""
import asyncio
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.models.lite_llm import LiteLlm
from google.adk.planners import BuiltInPlanner 
from google.genai import types

# 1. Configuration
OLLAMA_MODEL = LiteLlm(model="ollama_chat/llama3.2")
APP_NAME = "PlanningApp"

# 2. Define the Planning Agent
planner_agent = Agent(
    name="StrategicPlanner",
    model=OLLAMA_MODEL,
    instruction=(
        "You are a strategic project manager. When given a complex goal, "
        "your first priority is to break it down into a logical 4-step plan. "
        "List the steps clearly, then proceed to explain how you would execute them."
    ),
    planner=BuiltInPlanner(
        thinking_config=types.ThinkingConfig(
            include_thoughts=True,  
            thinking_budget=1024    
        )
    )
)

# 3. Generator Logic for Streamlit
async def execute_planning(user_query: str):
    session_service = InMemorySessionService()
    
    yield "🧠 Initializing Strategic Planner..."
    
    await session_service.create_session(
        user_id="u1", 
        session_id="plan_sess", 
        app_name=APP_NAME
    )
    
    runner = Runner(agent=planner_agent, session_service=session_service, app_name=APP_NAME)
    msg = types.Content(role='user', parts=[types.Part(text=user_query)])
    
    final_response = ""
    
    # Run the async loop
    async for event in runner.run_async(user_id="u1", session_id="plan_sess", new_message=msg):
        
        # Capture the model's internal 'thoughts' or 'plan' if the event type supports it
        # Many ADK versions emit a thought part before the final response part
        if hasattr(event, 'content') and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, 'thought') and part.thought:
                    yield "📝 **Constructing Plan:** " + part.thought[:100] + "..."
        
        if event.is_final_response():
            final_response = event.content.parts[0].text
            
    yield "✅ Plan finalized and strategy generated."
    yield final_response

# 4. Universal Entry Point
async def run_pattern(user_query: str):
    """Entry point for Streamlit dashboard."""
    return execute_planning(user_query)

if __name__ == "__main__":
    async def local_test():
        gen = await run_pattern("Plan a 3-day tech conference for 500 people.")
        async for update in gen:
            print(f"[Update]: {update}")
    
    asyncio.run(local_test())