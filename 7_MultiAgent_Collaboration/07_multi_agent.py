"""
Pattern: Multi-Agent Orchestration (The Manager)
Description: A Lead Agent (Manager) coordinates between multiple Specialist Agents.
"""
import asyncio
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.models.lite_llm import LiteLlm
from google.genai import types

# 1. Configuration
OLLAMA_MODEL = LiteLlm(model="ollama_chat/llama3.2")
APP_NAME = "MultiAgentApp"

# 2. Define the Specialist "Worker" Agents
researcher = Agent(
    name="Researcher",
    model=OLLAMA_MODEL,
    instruction="You are a research specialist. Provide factual data and historical context for any topic."
)

copywriter = Agent(
    name="Copywriter",
    model=OLLAMA_MODEL,
    instruction="You are a marketing copywriter. Turn dry facts into engaging, persuasive social media posts."
)

# 3. Define the "Manager" Agent
manager_agent = Agent(
    name="ProjectManager",
    model=OLLAMA_MODEL,
    instruction=(
        "You are the Lead Project Manager. You coordinate between the Researcher and the Copywriter. "
        "Review the outputs and provide a cohesive, professional summary."
    )
)

# 4. Generator Logic for Streamlit
async def execute_multi_agent(user_query: str):
    session_service = InMemorySessionService()
    
    # --- STEP 1: RESEARCH PHASE ---
    yield "🔍 **Phase 1:** Researcher is gathering factual data..."
    await session_service.create_session(user_id="u1", session_id="research_task", app_name=APP_NAME)
    runner_r = Runner(agent=researcher, session_service=session_service, app_name=APP_NAME)
    
    research_data = ""
    msg_r = types.Content(role='user', parts=[types.Part(text=user_query)])
    async for event in runner_r.run_async(user_id="u1", session_id="research_task", new_message=msg_r):
        if event.is_final_response():
            research_data = event.content.parts[0].text

    # --- STEP 2: COPYWRITING PHASE ---
    yield "✍️ **Phase 2:** Copywriter is transforming facts into engaging content..."
    await session_service.create_session(user_id="u1", session_id="writing_task", app_name=APP_NAME)
    runner_w = Runner(agent=copywriter, session_service=session_service, app_name=APP_NAME)
    
    marketing_copy = ""
    msg_w = types.Content(role='user', parts=[types.Part(text=f"Facts: {research_data}")])
    async for event in runner_w.run_async(user_id="u1", session_id="writing_task", new_message=msg_w):
        if event.is_final_response():
            marketing_copy = event.content.parts[0].text

    # --- STEP 3: MANAGER COMPILATION ---
    yield "📋 **Phase 3:** Project Manager is compiling the final report..."
    await session_service.create_session(user_id="u1", session_id="manager_final", app_name=APP_NAME)
    runner_m = Runner(agent=manager_agent, session_service=session_service, app_name=APP_NAME)
    
    final_report = ""
    manager_prompt = (
        f"Original Request: {user_query}\n\n"
        f"Researcher Output: {research_data}\n\n"
        f"Copywriter Output: {marketing_copy}\n\n"
        "Please finalize the report."
    )
    
    msg_m = types.Content(role='user', parts=[types.Part(text=manager_prompt)])
    async for event in runner_m.run_async(user_id="u1", session_id="manager_final", new_message=msg_m):
        if event.is_final_response():
            final_report = event.content.parts[0].text
            
    # Combine everything for a rich dashboard view
    yield (
        f"## 📊 Multi-Agent Collaboration Results\n\n"
        f"**Researcher Found:**\n{research_data[:200]}...\n\n"
        f"**Copywriter Drafted:**\n{marketing_copy[:200]}...\n\n"
        f"---\n"
        f"### 🏆 Final Manager Report\n{final_report}"
    )

# 5. Universal Entry Point
async def run_pattern(user_query: str):
    """Entry point for Streamlit dashboard."""
    return execute_multi_agent(user_query)

if __name__ == "__main__":
    async def local_test():
        gen = await run_pattern("The benefits of electric vehicles for city dwellers")
        async for update in gen:
            print(f"\n[Status]: {update}")
    
    asyncio.run(local_test())