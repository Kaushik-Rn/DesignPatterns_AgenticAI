"""
Pattern: Parallelization (The Octopus)
Description: Executes multiple agents simultaneously and aggregates their responses.
"""
import asyncio
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.models.lite_llm import LiteLlm
from google.genai import types

# 1. Configuration
OLLAMA_MODEL = LiteLlm(model="ollama_chat/llama3.2")
APP_NAME = "ParallelApp"

# 2. Define specialized "Reviewer" Agents
agents = [
    Agent(
        name="SecurityExpert",
        model=OLLAMA_MODEL,
        instruction="Analyze the input for security vulnerabilities or data privacy risks."
    ),
    Agent(
        name="PerformanceAnalyst",
        model=OLLAMA_MODEL,
        instruction="Analyze the input for speed, efficiency, and resource usage improvements."
    ),
    Agent(
        name="UXDesigner",
        model=OLLAMA_MODEL,
        instruction="Analyze the input for user experience, clarity, and ease of use."
    )
]

# 3. Helper to execute a single agent
async def call_single_agent(agent, query, session_service, index):
    session_id = f"parallel_sess_{index}"
    
    await session_service.create_session(
        user_id="u1", 
        session_id=session_id, 
        app_name=APP_NAME
    )
    
    runner = Runner(agent=agent, session_service=session_service, app_name=APP_NAME)
    msg = types.Content(role='user', parts=[types.Part(text=query)])
    
    response_text = ""
    async for event in runner.run_async(user_id="u1", session_id=session_id, new_message=msg):
        if event.is_final_response():
            response_text = event.content.parts[0].text
    
    return f"### 🛡️ {agent.name}\n{response_text}"

# 4. Generator Logic for Streamlit
async def execute_parallel(user_query: str):
    session_service = InMemorySessionService()
    
    # Update Status
    agent_names = ", ".join([a.name for a in agents])
    yield f"🐙 Launching {len(agents)} agents in parallel: {agent_names}..."
    
    # Create the concurrent tasks
    tasks = [
        call_single_agent(agent, user_query, session_service, i) 
        for i, agent in enumerate(agents)
    ]
    
    # Execute all tasks concurrently
    # Note: asyncio.gather waits for all to finish
    results = await asyncio.gather(*tasks)
    
    yield "✅ All agents finished. Aggregating reports..."
    
    combined_response = "\n\n---\n\n".join(results)
    
    # Final yield is the full response
    yield f"## Parallel Analysis Results\n\n{combined_response}"

# 5. Universal Entry Point
async def run_pattern(user_query: str):
    """Entry point for Streamlit dashboard."""
    return execute_parallel(user_query)

if __name__ == "__main__":
    # Local Test Script
    async def local_test():
        gen = await run_pattern("Build a website login system using only plain text files.")
        async for update in gen:
            print(update)
    
    asyncio.run(local_test())