# This agent doesn't just remember facts; it actually updates its own internal "Self-Correction" log.
# It analyzes its previous performance and adjusts its future instructions to avoid repeating mistakes.

# In the Google ADK, we implement this by creating a "Meta-Cognitive" loop where a "Learning Agent" writes new 
# system instructions based on past interaction history.

# Why this agent is advance?
# 1) Evolution: Instead of the agent being static, it evolves. If the user keeps correcting the agent's tone, 
# the "Teacher" agent will eventually bake that tone into the system instructions.

# 2) Meta-Programming: One LLM is effectively "programming" the prompt of another LLM - a concept known as Automated Prompt Engineering (APE).




"""
Pattern: Dynamic Adaptation (Learning)
Description: Agent analyzes its own history to update its instructions for better future performance.
"""
import asyncio
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.models.lite_llm import LiteLlm
from google.genai import types

# 1. Configuration
OLLAMA_MODEL = LiteLlm(model="ollama_chat/llama3.2")
APP_NAME = "LearningApp"

# 2. Define the Primary Agent
base_instruction = "You are a helpful assistant. Be concise."
primary_agent = Agent(
    name="AdaptiveAgent",
    model=OLLAMA_MODEL,
    instruction=base_instruction
)

# 3. Define the "Teacher" Agent
teacher_agent = Agent(
    name="InstructionOptimizer",
    model=OLLAMA_MODEL,
    instruction=(
        "You are an AI Trainer. Review the provided conversation snippet. "
        "Identify how the agent could better align with user preferences or tone. "
        "Output a single, improved system instruction starting with 'Updated Instruction: '."
    )
)

# 4. Generator Logic for Streamlit
async def execute_adaptation(user_query: str):
    session_service = InMemorySessionService()
    FIXED_SID = "learning_sess_001"
    
    # --- STEP 1: INTERACTION ---
    yield "🤖 Agent is generating a response..."
    await session_service.create_session(user_id="u1", session_id=FIXED_SID, app_name=APP_NAME)
    runner_p = Runner(agent=primary_agent, session_service=session_service, app_name=APP_NAME)
    
    response = ""
    msg = types.Content(role='user', parts=[types.Part(text=user_query)])
    async for event in runner_p.run_async(user_id="u1", session_id=FIXED_SID, new_message=msg):
        if event.is_final_response():
            response = event.content.parts[0].text

    # --- STEP 2: LEARNING (The Adaptation Loop) ---
    yield "🧠 Meta-Cognition: Teacher agent is evaluating performance..."
    
    history_context = f"User said: {user_query}\nAgent replied: {response}"
    learned_instruction = ""
    
    await session_service.create_session(user_id="u1", session_id="meta_sess", app_name=APP_NAME)
    runner_t = Runner(agent=teacher_agent, session_service=session_service, app_name=APP_NAME)
    
    t_msg = types.Content(role='user', parts=[types.Part(text=f"Optimize instruction based on this interaction: {history_context}")])
    async for event in runner_t.run_async(user_id="u1", session_id="meta_sess", new_message=t_msg):
        if event.is_final_response():
            learned_instruction = event.content.parts[0].text

    # --- STEP 3: OUTPUT ---
    yield "✅ Learning cycle complete. Improvements logged."
    
    yield (
        f"### 🤖 Current Response\n{response}\n\n"
        f"---\n"
        f"### 💡 Adaptive Learning (Teacher's Note)\n"
        f"The InstructionOptimizer suggested the following for future sessions:\n\n"
        f"> {learned_instruction}"
    )

# 5. Universal Entry Point
async def run_pattern(user_query: str):
    """Entry point for Streamlit dashboard."""
    return execute_adaptation(user_query)

if __name__ == "__main__":
    async def local_test():
        gen = await run_pattern("Write a short email. I hate formal greetings.")
        async for update in gen:
            print(f"\n{update}")
    
    asyncio.run(local_test())