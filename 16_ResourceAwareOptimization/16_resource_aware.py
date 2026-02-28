"""
Why this is a "Smart" Pattern for your Dashboard:
1) Cost Efficiency: It teaches the user that "One size does NOT fit all." It demonstrates the balance between local compute (Ollama) and cloud compute (Gemini).
2) Latency Optimization: For simple greetings, the response is near-instant because it skips the cloud handshake and complex reasoning tokens.
3) Transparency: By showing the "Profiling..." status, the user understands why the system is choosing a specific model.
"""

"""
Dashboard Test Case:

Eco Tier: Type "What is 2+2?" -> The status will show ⚡ ECO (Llama 3.2).
Premium Tier: Type "Explain the logical paradox of the Ship of Theseus and apply it to modern software refactoring." -> The status will flip to 💎 PREMIUM (Gemini 2.0).
"""

"""
Pattern: Resource-Aware Optimization
Description: Dynamically selects models based on task complexity to optimize cost and latency.
"""
import asyncio
import streamlit as st
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.models.lite_llm import LiteLlm
from google.genai import types

# 1. Configuration - Two distinct model tiers
# Note: Ensure you have your Google API Key set in environment for Gemini
FAST_MODEL = LiteLlm(model="ollama_chat/llama3.2")      # Local / Low Latency
SMART_MODEL = LiteLlm(model="google/gemini-2.0-flash")  # Cloud / High Reasoning
APP_NAME = "ResourceAwareApp"

# 2. Define specialized Agents
quick_responder = Agent(
    name="QuickBot", 
    model=FAST_MODEL, 
    instruction="You are a fast, concise assistant for simple queries."
)

deep_thinker = Agent(
    name="ReasoningBot", 
    model=SMART_MODEL, 
    instruction="You are a high-reasoning engine for complex logic, coding, and strategy."
)

# 3. Generator Logic for Streamlit
async def execute_resource_aware(user_query: str):
    session_service = InMemorySessionService()
    SID = "res_sess"
    
    yield "🔍 Profiling task complexity and compute requirements..."
    
    # --- COMPLEXITY ANALYSIS LOGIC ---
    # In a real app, this could be a 'Classifier' LLM call itself.
    # Here we use heuristic analysis for demonstration.
    hard_keywords = ["logic", "puzzle", "code", "complex", "strategy", "analyze", "math"]
    is_complex = any(k in user_query.lower() for k in hard_keywords) or len(user_query) > 150
    
    selected_agent = deep_thinker if is_complex else quick_responder
    tier_label = "💎 PREMIUM (Gemini 2.0)" if is_complex else "⚡ ECO (Llama 3.2)"
    
    yield f"🚀 Routing to **{tier_label}** based on performance profile..."
    await asyncio.sleep(0.8) # Simulate routing overhead
    
    await session_service.create_session(user_id="u1", session_id=SID, app_name=APP_NAME)
    runner = Runner(agent=selected_agent, session_service=session_service, app_name=APP_NAME)
    
    response = ""
    msg = types.Content(role='user', parts=[types.Part(text=user_query)])
    
    async for event in runner.run_async(user_id="u1", session_id=SID, new_message=msg):
        if event.is_final_response():
            response = event.content.parts[0].text
            
    yield f"### ⚖️ Resource Allocation: {tier_label}\n\n{response}"

# 4. Universal Entry Point
async def run_pattern(user_query: str):
    """Entry point for Streamlit dashboard."""
    return execute_resource_aware(user_query)

if __name__ == "__main__":
    async def local_test():
        # Test Simple
        print("--- Testing Simple ---")
        gen1 = await run_pattern("Hi there!")
        async for update in gen1: print(update)
        
        # Test Complex
        print("\n--- Testing Complex ---")
        gen2 = await run_pattern("Write a complex python script to analyze stock market volatility.")
        async for update in gen2: print(update)
    
    asyncio.run(local_test())