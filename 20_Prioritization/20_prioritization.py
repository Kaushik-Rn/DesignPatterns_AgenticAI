"""
Why this is a powerful addition to your Dashboard:
1) Intelligence over Automation: It demonstrates that the agent doesn't just "do things"—it decides what is worth doing.
2) Operational Scenarios: This is highly relatable for business users. It shows how an AI could act as a triage nurse for customer support tickets or a technical lead for GitHub issues.
3) Dynamic Reordering: In the dashboard, you can provide a list of messy, unordered tasks and watch the agent output a structured, professional roadmap.
"""

"""
Dashboard Test Case:

Prompt: > "Tasks: Update documentation, Fix security vulnerability in payment gateway, Answer a general question about office hours, Address server downtime."
Result: The agent should move the "Security Vulnerability" and "Server Downtime" to the top (Critical/High) and push "Documentation" and "Office Hours" to the bottom.
"""

"""
Pattern: Prioritization (Queue Management)
Description: Sorts multiple user requests by importance and urgency using an Eisenhower-style logic.
"""
import asyncio
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.models.lite_llm import LiteLlm
from google.genai import types

# 1. Configuration
OLLAMA_MODEL = LiteLlm(model="ollama_chat/llama3.2")
APP_NAME = "PriorityApp"

# 2. Define the Sorting Agent
sorter = Agent(
    name="PrioritySorter",
    model=OLLAMA_MODEL,
    instruction=(
        "You are a Project Management specialist. Given a list of tasks or user requests: "
        "1. Categorize each into: Critical, High, Medium, or Low.\n"
        "2. Sort the list so Critical items appear first.\n"
        "3. For each item, provide a one-sentence 'Reasoning' based on urgency and impact.\n"
        "Format the output as a clean, markdown-friendly list."
    )
)

# 3. Generator Logic for Streamlit
async def execute_prioritization(user_query: str):
    session_service = InMemorySessionService()
    SID = "p_sess"
    
    yield "📋 **Step 1:** Ingesting task list and analyzing request context..."
    
    await session_service.create_session(user_id="u1", session_id=SID, app_name=APP_NAME)
    runner = Runner(agent=sorter, session_service=session_service, app_name=APP_NAME)
    
    yield "⚖️ **Step 2:** Applying Eisenhower Matrix logic to determine importance vs. urgency..."
    
    response = ""
    msg = types.Content(role='user', parts=[types.Part(text=user_query)])
    
    async for event in runner.run_async(user_id="u1", session_id=SID, new_message=msg):
        if event.is_final_response():
            response = event.content.parts[0].text
            
    yield "✅ **Step 3:** Task queue re-ordered and ready for execution."
    yield f"### 📊 Optimized Prioritization Matrix\n\n{response}"

# 4. Universal Entry Point
async def run_pattern(user_query: str):
    """Entry point for Streamlit dashboard."""
    return execute_prioritization(user_query)

if __name__ == "__main__":
    async def local_test():
        test_tasks = """
        1. Fix a minor typo in the 'About' page.
        2. Resolve a database connection leak causing 500 errors for all users.
        3. Research potential color schemes for next year's marketing campaign.
        4. Reset the password for the CEO who is locked out of their account.
        """
        gen = await run_pattern(test_tasks)
        async for update in gen:
            print(f"\n{update}")
    
    asyncio.run(local_test())