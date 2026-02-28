# How to test this in your Dashboard:
# This pattern is unique because it requires two separate runs to see the magic:

# Turn 1: Select "08: Memory Management" and type:
# “My name is Alex and I prefer coding in Python.”
# Click Run. The agent will say hello.
# Turn 2: Change the prompt to:
# “What is my name and what language should we use for our project?”
# Click Run again.
# The Result: Because we stored the InMemorySessionService in st.session_state, the agent will correctly identify you as Alex and suggest Python, even though the script technically "restarted."


"""
Pattern: Memory (Context Persistence)
Description: Demonstrates how to maintain state and recall information over a multi-turn conversation.
"""
import asyncio
import streamlit as st
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.models.lite_llm import LiteLlm
from google.genai import types

# 1. Configuration
OLLAMA_MODEL = LiteLlm(model="ollama_chat/llama3.2")
APP_NAME = "MemoryApp"

# 2. Define the Agent
memory_agent = Agent(
    name="MemoryAgent",
    model=OLLAMA_MODEL,
    instruction=(
        "You are a helpful assistant with a long-term memory. "
        "Pay close attention to facts the user shared in previous messages. "
        "If they ask a follow-up question, use that context to provide a personalized answer."
    )
)

# 3. Generator Logic for Streamlit
async def execute_memory(user_query: str):
    # --- CRITICAL: Persist the Session Service in Streamlit State ---
    # This prevents the memory from being wiped every time the "Run" button is clicked.
    if "agent_memory_service" not in st.session_state:
        st.session_state.agent_memory_service = InMemorySessionService()
    
    session_service = st.session_state.agent_memory_service
    FIXED_SESSION_ID = "persistent_user_123"
    USER_ID = "u1"

    yield "🧠 Accessing persistent memory bank..."

    # Check if session exists, create if not
    try:
        await session_service.create_session(
            user_id=USER_ID, 
            session_id=FIXED_SESSION_ID, 
            app_name=APP_NAME
        )
    except Exception:
        # Session already exists, which is what we want for memory!
        pass
    
    runner = Runner(agent=memory_agent, session_service=session_service, app_name=APP_NAME)
    msg = types.Content(role='user', parts=[types.Part(text=user_query)])
    
    final_response = ""
    async for event in runner.run_async(user_id=USER_ID, session_id=FIXED_SESSION_ID, new_message=msg):
        if event.is_final_response():
            final_response = event.content.parts[0].text
            
    yield f"✅ Memory recalled for Session: `{FIXED_SESSION_ID}`"
    yield final_response

# 4. Universal Entry Point
async def run_pattern(user_query: str):
    """Entry point for Streamlit dashboard."""
    return execute_memory(user_query)

if __name__ == "__main__":
    # Local Test
    async def local_test():
        gen = await run_pattern("Hi, my name is Alex.")
        async for update in gen: print(update)
    asyncio.run(local_test())