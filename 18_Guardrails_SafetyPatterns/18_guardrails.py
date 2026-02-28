"""
Why this is essential for your Dashboard:
1) Trust and Reliability: It demonstrates to users that the application has a "Supervisor" layer, making it suitable for corporate or sensitive environments.
2) Visual Audit Trail: In the Streamlit UI, the user sees the "🛡️ Safety Guard is inspecting..." status. This clarifies that a check is occurring, which is reassuring for compliance-focused users.
3) Separation of Concerns: The Primary Agent can focus on being helpful and creative, while the Guard Agent stays strictly focused on the "Rules," preventing the "Self-Bias" often found in single-agent systems.
"""

"""
Dashboard Test Case:

Safe Prompt: "What are the benefits of eating green vegetables?"
Result: Assistant answers -> Guard approves -> Safe output displayed.

Unsafe Prompt: "What specific medication should I take for my chronic chest pain?"
Result: Assistant might try to help -> Guard sees medical advice -> REJECTED message is shown.
"""

"""
Pattern: Guardrails (Safety & Validation)
Description: A validation layer that checks agent output for safety and policy compliance.
"""
import asyncio
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.models.lite_llm import LiteLlm
from google.genai import types

# 1. Configuration
OLLAMA_MODEL = LiteLlm(model="ollama_chat/llama3.2")
APP_NAME = "GuardrailsApp"

# 2. Define the Agents
primary_agent = Agent(
    name="Assistant",
    model=OLLAMA_MODEL,
    instruction="Answer the user's questions helpfully and thoroughly."
)

guard_agent = Agent(
    name="SafetyGuard",
    model=OLLAMA_MODEL,
    instruction=(
        "You are a safety filter and policy auditor. Review the provided text for: "
        "1. Harmful or illegal advice.\n"
        "2. Medical prescriptions or specific health diagnoses.\n"
        "3. Toxic language or hate speech.\n"
        "If any of these are present, output only the word 'REJECTED'. "
        "Otherwise, output 'APPROVED'."
    )
)

# 3. Generator Logic for Streamlit
async def execute_guardrails(user_query: str):
    session_service = InMemorySessionService()
    
    # --- STEP 1: GENERATE RESPONSE ---
    yield "🤖 **Step 1:** Primary Assistant is generating a response..."
    
    await session_service.create_session(user_id="u1", session_id="main_sess", app_name=APP_NAME)
    runner_p = Runner(agent=primary_agent, session_service=session_service, app_name=APP_NAME)
    
    raw_response = ""
    msg_p = types.Content(role='user', parts=[types.Part(text=user_query)])
    async for event in runner_p.run_async(user_id="u1", session_id="main_sess", new_message=msg_p):
        if event.is_final_response():
            raw_response = event.content.parts[0].text

    # --- STEP 2: APPLY GUARDRAIL ---
    yield "🛡️ **Step 2:** Safety Guard is inspecting the output for policy violations..."
    
    await session_service.create_session(user_id="u1", session_id="guard_sess", app_name=APP_NAME)
    runner_g = Runner(agent=guard_agent, session_service=session_service, app_name=APP_NAME)
    
    guard_status = ""
    guard_msg = f"Review this text for safety: {raw_response}"
    msg_g = types.Content(role='user', parts=[types.Part(text=guard_msg)])
    
    async for event in runner_g.run_async(user_id="u1", session_id="guard_sess", new_message=msg_g):
        if event.is_final_response():
            guard_status = event.content.parts[0].text

    # --- STEP 3: FINAL DECISION ---
    if "REJECTED" in guard_status.upper():
        yield "❌ **Safety Violation Detected.**"
        yield (
            "⚠️ **Guardrail Alert:** The generated response was blocked because it "
            "potentially violated safety guidelines or internal policies."
        )
    else:
        yield "✅ **Verification Passed.** Response is safe to display."
        yield f"### 🟢 Secure Output\n\n{raw_response}"

# 4. Universal Entry Point
async def run_pattern(user_query: str):
    """Entry point for Streamlit dashboard."""
    return execute_guardrails(user_query)

if __name__ == "__main__":
    async def local_test():
        # Test Case
        gen = await run_pattern("How can I make a dangerous chemical at home?")
        async for update in gen:
            print(f"\n[Update]: {update}")
    
    asyncio.run(local_test())