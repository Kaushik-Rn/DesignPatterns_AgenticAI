"""
Pattern: Reflection (Self-Correction)
Description: A two-stage process where a draft is critiqued and then improved.
"""
import asyncio
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.models.lite_llm import LiteLlm
from google.genai import types

# 1. Configuration
OLLAMA_MODEL = LiteLlm(model="ollama_chat/llama3.2")
APP_NAME = "ReflectionApp"

# 2. Define specialized Agents
writer_agent = Agent(
    name="CreativeWriter",
    model=OLLAMA_MODEL,
    instruction="You are a professional writer. Create a concise, high-quality draft based on the user's topic."
)

critic_agent = Agent(
    name="EditorialCritic",
    model=OLLAMA_MODEL,
    instruction=(
        "You are a strict editor. Review the provided draft. "
        "Point out 2 specific weaknesses and suggest how to make it more impactful."
    )
)

# 3. Execution Logic (The Generator)
async def execute_reflection(user_query: str):
    session_service = InMemorySessionService()
    
    # --- STEP 1: INITIAL DRAFT ---
    yield "📝 Generating initial draft..."
    await session_service.create_session(user_id="u1", session_id="s1_draft", app_name=APP_NAME)
    runner_w = Runner(agent=writer_agent, session_service=session_service, app_name=APP_NAME)
    
    draft_text = ""
    msg1 = types.Content(role='user', parts=[types.Part(text=user_query)])
    async for event in runner_w.run_async(user_id="u1", session_id="s1_draft", new_message=msg1):
        if event.is_final_response():
            draft_text = event.content.parts[0].text

    # --- STEP 2: CRITIQUE ---
    yield "🧐 Sending draft to Editorial Critic for feedback..."
    await session_service.create_session(user_id="u1", session_id="s2_critique", app_name=APP_NAME)
    runner_c = Runner(agent=critic_agent, session_service=session_service, app_name=APP_NAME)
    
    critique_text = ""
    msg2 = types.Content(role='user', parts=[types.Part(text=f"Please critique this draft:\n\n{draft_text}")])
    async for event in runner_c.run_async(user_id="u1", session_id="s2_critique", new_message=msg2):
        if event.is_final_response():
            critique_text = event.content.parts[0].text

    # --- STEP 3: FINAL POLISH ---
    yield "✨ Incorporating feedback and polishing the final version..."
    await session_service.create_session(user_id="u1", session_id="s3_final", app_name=APP_NAME)
    
    final_polish_msg = (
        f"Original Draft: {draft_text}\n\n"
        f"Critic Feedback: {critique_text}\n\n"
        f"Please rewrite the draft incorporating the feedback."
    )
    
    final_text = ""
    msg3 = types.Content(role='user', parts=[types.Part(text=final_polish_msg)])
    async for event in runner_w.run_async(user_id="u1", session_id="s3_final", new_message=msg3):
        if event.is_final_response():
            final_text = event.content.parts[0].text
            
    # Final yield is the full Markdown report
    yield (
        f"## Reflection Process Complete\n\n"
        f"### 📝 Initial Draft\n{draft_text}\n\n"
        f"---\n"
        f"### 🧐 Critic Feedback\n{critique_text}\n\n"
        f"---\n"
        f"### ✨ Final Polished Version\n{final_text}"
    )

# 4. Universal Entry Point
async def run_pattern(user_query: str):
    """Entry point for Streamlit dashboard."""
    return execute_reflection(user_query)

if __name__ == "__main__":
    # Local Test
    async def local_test():
        gen = await run_pattern("Write a short pitch for a Martian colony.")
        async for update in gen:
            print(f"\n[Status]: {update}")
    
    asyncio.run(local_test())