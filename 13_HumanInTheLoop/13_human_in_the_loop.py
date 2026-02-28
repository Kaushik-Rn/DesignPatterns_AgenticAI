""" 
Why this is a "Pattern" for your Dashboard:
1) Asynchronous Gating: In a real production environment, this agent would save its state to a database and wait. In our dashboard, we simulate this by letting the user "re-trigger" the same session with a keyword.
2) Safety First: It demonstrates that the AI doesn't have "write access" to the world without a human "click."
3) Iterative Refinement: If the human doesn't like the draft, they simply provide feedback instead of saying "APPROVED," allowing the agent to refine its work in the next turn.
 """

""" 
Dashboard Test Instructions:

Prompt 1: "Draft a resignation letter to my company, keeping it professional but firm."
Result: You get a draft and a "Pause" notice.

Prompt 2: Type "APPROVED" in that same text area and click Run.
Result: The status changes to "Action Executed," simulating the actual sending of the email.
"""

"""
Pattern: Human-in-the-Loop (Approval)
Description: Agent pauses high-stakes execution to wait for user verification or feedback.
"""
import asyncio
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.models.lite_llm import LiteLlm
from google.genai import types

# 1. Configuration
OLLAMA_MODEL = LiteLlm(model="ollama_chat/llama3.2")
APP_NAME = "HITL_App"

draft_agent = Agent(
    name="EmailDrafter",
    model=OLLAMA_MODEL,
    instruction=(
        "You are an executive assistant. Your task is to draft a formal email. "
        "Do not send it. Present it clearly for review. "
        "Always start the response with '📝 PROPOSED DRAFT:'."
    )
)

# 2. Generator Logic for Streamlit
async def execute_hitl(user_query: str):
    session_service = InMemorySessionService()
    SID = "hitl_sess"
    
    # Check for approval keyword
    if user_query.strip().upper().startswith("APPROVED"):
        yield "🚦 Checking human authorization credentials..."
        await asyncio.sleep(0.5)
        yield "📧 **Action Executed:** The email has been dispatched via the SMTP gateway."
        yield "✅ Success: Task finalized with human sign-off."
        return

    # --- STEP 1: PREPARE DRAFT ---
    yield "🧠 Agent is drafting the proposal for your review..."
    
    await session_service.create_session(user_id="u1", session_id=SID, app_name=APP_NAME)
    runner = Runner(agent=draft_agent, session_service=session_service, app_name=APP_NAME)
    
    draft = ""
    msg = types.Content(role='user', parts=[types.Part(text=user_query)])
    async for event in runner.run_async(user_id="u1", session_id="hitl_sess", new_message=msg):
        if event.is_final_response():
            draft = event.content.parts[0].text

    yield "⏸️ Execution paused: Awaiting human intervention."
    
    yield (
        f"### 📬 Draft for Review\n{draft}\n\n"
        f"---\n"
        f"### ⚖️ Decision Required\n"
        f"If this looks good, please type **'APPROVED'** in the prompt box and click run again. "
        f"Otherwise, provide feedback to modify the draft."
    )

# 3. Universal Entry Point
async def run_pattern(user_query: str):
    """Entry point for Streamlit dashboard."""
    return execute_hitl(user_query)

if __name__ == "__main__":
    async def local_test():
        # Test Draft Phase
        gen = await run_pattern("Write an email to my boss about my promotion.")
        async for update in gen: print(update)
    
    asyncio.run(local_test())