""" 
Why this is effective for the Dashboard:
1) Constraint Validation: If you prompt the agent with: "Write a 100-word story about a cat, but do not use the word 'meow' or 'feline'," update the Auditor to check those specific negatives.
2) Objective Scoring: It provides the user with a numerical or qualitative "score" on how well the AI actually listened.
3) Separation of Concerns: By using two different agents, you bypass the "Self-Bias" problem where an LLM is often unable to see its own mistakes in the same turn.
 """

"""
Pattern: Monitoring (Goal Tracking)
Description: An internal auditor checks if the agent's output satisfies the user's specific success criteria.
"""
import asyncio
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.models.lite_llm import LiteLlm
from google.genai import types

# 1. Configuration
OLLAMA_MODEL = LiteLlm(model="ollama_chat/llama3.2")
APP_NAME = "MonitoringApp"

# 2. Define the Main Worker and the Monitor
worker_agent = Agent(
    name="TaskWorker",
    model=OLLAMA_MODEL,
    instruction="Execute the user's request thoroughly. Ensure you follow all constraints mentioned in the prompt."
)

monitor_agent = Agent(
    name="GoalAuditor",
    model=OLLAMA_MODEL,
    instruction=(
        "You are a strict Quality Auditor. Compare the User's original Goal with the Agent's actual Response. "
        "1. Rate the alignment from 1-10.\n"
        "2. Check if specific constraints (length, tone, facts) were met.\n"
        "3. If the score is below 8, identify exactly what is missing."
    )
)

# 3. Generator Logic for Streamlit
async def execute_monitoring(user_query: str):
    session_service = InMemorySessionService()
    SID = "monitor_sess_001"
    
    # --- STEP 1: EXECUTION ---
    yield "🛠️ **Worker Agent:** Executing primary task..."
    await session_service.create_session(user_id="u1", session_id=SID, app_name=APP_NAME)
    runner_w = Runner(agent=worker_agent, session_service=session_service, app_name=APP_NAME)
    
    worker_response = ""
    msg_w = types.Content(role='user', parts=[types.Part(text=user_query)])
    async for event in runner_w.run_async(user_id="u1", session_id=SID, new_message=msg_w):
        if event.is_final_response():
            worker_response = event.content.parts[0].text

    # --- STEP 2: MONITORING ---
    yield "🔍 **Auditor Agent:** Evaluating alignment with original goals..."
    
    audit_msg = (
        f"USER GOAL: {user_query}\n\n"
        f"AGENT RESPONSE: {worker_response}\n\n"
        "Critique the response based on the goal."
    )
    
    audit_report = ""
    await session_service.create_session(user_id="u1", session_id="audit_log", app_name=APP_NAME)
    runner_m = Runner(agent=monitor_agent, session_service=session_service, app_name=APP_NAME)
    
    msg_m = types.Content(role='user', parts=[types.Part(text=audit_msg)])
    async for event in runner_m.run_async(user_id="u1", session_id="audit_log", new_message=msg_m):
        if event.is_final_response():
            audit_report = event.content.parts[0].text

    # Final Output
    yield "✅ Monitoring cycle complete."
    yield (
        f"### 🛠️ Worker Output\n{worker_response}\n\n"
        f"---\n"
        f"### 🔍 Auditor Report & Score\n{audit_report}"
    )

# 4. Universal Entry Point
async def run_pattern(user_query: str):
    """Entry point for Streamlit dashboard."""
    return execute_monitoring(user_query)

if __name__ == "__main__":
    async def local_test():
        gen = await run_pattern("Write a 3-sentence summary of the moon landing for a 5-year old.")
        async for update in gen:
            print(f"\n{update}")
    
    asyncio.run(local_test())