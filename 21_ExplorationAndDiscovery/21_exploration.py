"""
Why this pattern is useful?

This pattern prevents hallucinations by forcing the agent to explicitly identify knowledge gaps before 
attempting a complex answer. 

It provides transparency to the user by revealing the agent's internal logic and the specific research 
required for a high-quality response. 

Ultimately, it serves as a strategic foundation for multi-step workflows, ensuring the agent prioritizes
accurate discovery over immediate, surface-level guesses.
"""

"""
Pattern: Exploration (Recursive Discovery)
Description: Agent proactively identifies gaps in its knowledge and explores them.
"""
import asyncio
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.models.lite_llm import LiteLlm
from google.genai import types

import nest_asyncio
nest_asyncio.apply()

# 1. Define the Model
OLLAMA_MODEL = LiteLlm(model="ollama_chat/llama3.2")
APP_NAME = "ExplorationApp"

# 2. Define the Agent
explorer = Agent(
    name="Explorer",
    model=OLLAMA_MODEL,
    instruction=(
        "You are a recursive discovery agent. Analyze the user's prompt. "
        "1. List 3 specific things you already know about this topic. "
        "2. List 3 critical knowledge gaps or 'unknowns' you would need to research to provide a perfect answer. "
        "Format the output as a clean markdown roadmap."
    )
)

async def execute_exploration(user_query: str):
    """Asynchronous generator that yields status updates and the final response."""
    session_service = InMemorySessionService()
    
    # --- Step 1: Initialization ---
    yield "🔍 Analyzing prompt for knowledge gaps..."
    await session_service.create_session(user_id="u1", session_id="x_sess", app_name=APP_NAME)
    runner = Runner(agent=explorer, session_service=session_service, app_name=APP_NAME)
    
    # --- Step 2: Recursive Discovery ---
    yield "🧠 Identifying knowns vs. unknowns..."
    
    response_text = ""
    msg = types.Content(role='user', parts=[types.Part(text=user_query)])
    
    async for event in runner.run_async(user_id="u1", session_id="x_sess", new_message=msg):
        if event.is_final_response():
            response_text = event.content.parts[0].text
            
    # --- Step 3: Final Yield ---
    yield f"### 🧭 Exploration Roadmap\n{response_text}"

async def run_pattern(user_query: str):
    """Entry point for the Streamlit dashboard."""
    # Returns the generator object
    return execute_exploration(user_query)

if __name__ == "__main__":
    # Local testing logic
    async def main():
        gen = await run_pattern("Suggest 5 unconventional use cases for LLMs in marine biology.")
        async for update in gen:
            print(update)
    
    asyncio.run(main())