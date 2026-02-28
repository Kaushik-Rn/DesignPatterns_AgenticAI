"""
Why this is essential for your Dashboard:
1) Transparency of Logic: It reveals the "Black Box" of AI. Users can see exactly where the model might have misunderstood a premise.
2) Error Prevention: This is the best defense against "trick questions." In your test query ("If I have three apples and you take away two, how many apples do you have?"), a "lazy" AI says 1, but a reasoning AI realizes you now have the 2 apples you took.
3) Structured Output: By enforcing the THOUGHT PROCESS and FINAL ANSWER headers, your dashboard can easily distinguish between the scratchpad and the result.
"""


"""
Pattern: Reasoning (Chain of Thought)
Description: Forces the agent to output its step-by-step logic before giving a final answer.
"""
import asyncio
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.models.lite_llm import LiteLlm
from google.genai import types

# 1. Configuration
OLLAMA_MODEL = LiteLlm(model="ollama_chat/llama3.2")
APP_NAME = "ReasoningApp"

# 2. Define the Reasoning Agent
reasoning_agent = Agent(
    name="Logician",
    model=OLLAMA_MODEL,
    instruction=(
        "You are a logical reasoning expert. For every query: "
        "1. Start with a section titled '🧠 THOUGHT PROCESS' where you break down the logic "
        "step-by-step, identifying potential pitfalls or hidden constraints. "
        "2. Follow with a section titled '🎯 FINAL ANSWER'. "
        "Do not skip the thought process, as it is the foundation of your accuracy."
    )
)

# 3. Generator Logic for Streamlit
async def execute_reasoning(user_query: str):
    session_service = InMemorySessionService()
    SID = "reason_sess"
    
    yield "🧠 Engaging high-reasoning 'Inner Monologue' mode..."
    
    await session_service.create_session(user_id="u1", session_id=SID, app_name=APP_NAME)
    runner = Runner(agent=reasoning_agent, session_service=session_service, app_name=APP_NAME)
    
    msg = types.Content(role='user', parts=[types.Part(text=user_query)])
    
    response = ""
    # We use the generator to show that the agent is "thinking"
    async for event in runner.run_async(user_id="u1", session_id=SID, new_message=msg):
        if event.is_final_response():
            response = event.content.parts[0].text
            
    yield "✅ Logical deduction complete."
    yield f"{response}"

# 4. Universal Entry Point
async def run_pattern(user_query: str):
    """Entry point for Streamlit dashboard."""
    return execute_reasoning(user_query)

if __name__ == "__main__":
    async def local_test():
        test_query = "If I have three apples and you take away two, how many apples do you have?"
        gen = await run_pattern(test_query)
        async for update in gen:
            print(f"\n[Update]: {update}")
    
    asyncio.run(local_test())