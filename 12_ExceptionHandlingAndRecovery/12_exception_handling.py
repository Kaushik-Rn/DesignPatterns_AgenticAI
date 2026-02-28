"""
Why this is essential for your Dashboard:
1) User Confidence: Instead of the Streamlit app showing a red "Internal Error" box that stops the whole app, the user sees a controlled "Recovery Mode" message.
2) Debuggability: By yielding the error message directly to the UI, you don't have to check the terminal logs to see why a request failed.
3) The "Force Fail" Toggle: The simulation logic (if "force fail" in user_query) is great for demos. It proves the recovery logic works without you actually having to unplug your internet or crash Ollama.
 """

""" 
Dashboard Test Case:
Normal Test: Type "Hello" $\rightarrow$ See standard success.
Failure Test: Type "Please force fail this" $\rightarrow$ Watch the status change from "📡 Sending..." to "⚠️ Error Detected!" and finally to the "🛡️ Recovery Mode" report.
 """

"""
Pattern: Exception Handling (Recovery)
Description: Gracefully handles model/tool failures and provides fallback logic.
"""
import asyncio
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.models.lite_llm import LiteLlm
from google.genai import types

# 1. Configuration
OLLAMA_MODEL = LiteLlm(model="ollama_chat/llama3.2")
APP_NAME = "RecoveryApp"

primary_agent = Agent(
    name="PrimaryAgent",
    model=OLLAMA_MODEL,
    instruction="Try to answer the user query accurately."
)

# 2. Generator Logic for Streamlit
async def execute_recovery(user_query: str):
    session_service = InMemorySessionService()
    SID = "recovery_sess"
    
    yield "🛡️ Initializing execution with safety wrappers..."
    
    try:
        # --- ATTEMPT EXECUTION ---
        await session_service.create_session(user_id="u1", session_id=SID, app_name=APP_NAME)
        runner = Runner(agent=primary_agent, session_service=session_service, app_name=APP_NAME)
        
        # Simulated Failure Trigger
        if "force fail" in user_query.lower():
            yield "🧨 Simulating critical system failure..."
            await asyncio.sleep(1) # Dramatic pause for the UI
            raise Exception("SIMULATED_MODEL_TIMEOUT: Connection to Ollama lost.")

        response = ""
        yield "📡 Sending request to primary LLM..."
        
        async for event in runner.run_async(user_id="u1", session_id=SID, new_message=types.Content(role='user', parts=[types.Part(text=user_query)])):
            if event.is_final_response():
                response = event.content.parts[0].text
        
        yield "✅ Execution successful."
        yield f"**Status: Success**\n\n{response}"

    except Exception as e:
        # --- RECOVERY LOGIC ---
        yield "⚠️ **Error Detected!** Engaging recovery protocols..."
        await asyncio.sleep(1)
        
        fallback_msg = (
            "## 🛡️ Recovery Mode Activated\n\n"
            f"The primary agent encountered an error: `{str(e)}`.\n\n"
            "**System Fallback:** I am currently experiencing technical difficulties with the primary model. "
            "However, the safety layer successfully prevented a system crash. Please try again or check your local Ollama connection."
        )
        yield fallback_msg

# 3. Universal Entry Point
async def run_pattern(user_query: str):
    """Entry point for Streamlit dashboard."""
    return execute_recovery(user_query)

if __name__ == "__main__":
    async def local_test():
        # Test failure case
        gen = await run_pattern("force fail")
        async for update in gen:
            print(update)
    
    asyncio.run(local_test())