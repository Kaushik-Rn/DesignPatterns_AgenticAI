"""
Why this is essential for your Dashboard:
1) Continuous Improvement: This pattern allows you to demonstrate "Self-Correction." If the score is too low, you could theoretically trigger a re-generation loop.
2) Objective Visuals: By providing a structured ⭐ score in the UI, you give the user an immediate sense of the system's reliability.
3) Rubric-Based Trust: It shows that the AI isn't just "talking"—it's being held to a standard of Clarity, Accuracy, and Tone.
"""

"""
Dashboard Test Case:

Prompt: "Explain quantum entanglement to a 10-year-old."
Watch the Process: The Worker will explain it, and the Judge will likely penalize the Worker if the explanation is too technical (Clarity) or too dry (Tone).
"""

"""
Pattern: Evaluation (LLM-as-a-Judge)
Description: An evaluator agent scores the primary agent's output against a specific rubric.
"""
import asyncio
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.models.lite_llm import LiteLlm
from google.genai import types

# 1. Configuration
OLLAMA_MODEL = LiteLlm(model="ollama_chat/llama3.2")
APP_NAME = "EvaluationApp"

# 2. Define the Agents
worker = Agent(
    name="Worker", 
    model=OLLAMA_MODEL, 
    instruction="Provide a detailed, accurate, and easy-to-understand explanation of the user's topic."
)

evaluator = Agent(
    name="Evaluator", 
    model=OLLAMA_MODEL, 
    instruction=(
        "You are a quality assurance judge. Rate the provided explanation on a scale of 1-5 for: "
        "\n1. Clarity (Is it easy to follow?) "
        "\n2. Accuracy (Does it seem factually sound?) "
        "\n3. Tone (Is it appropriate for the context?) "
        "\nProvide a brief justification for each score."
    )
)

# 3. Generator Logic for Streamlit
async def execute_evaluation(user_query: str):
    session_service = InMemorySessionService()
    
    # --- STEP 1: GENERATION ---
    yield "🛠️ **Step 1:** Worker Agent is drafting the explanation..."
    
    await session_service.create_session(user_id="u1", session_id="w_sess", app_name=APP_NAME)
    runner_w = Runner(agent=worker, session_service=session_service, app_name=APP_NAME)
    
    work_out = ""
    msg_w = types.Content(role='user', parts=[types.Part(text=user_query)])
    async for event in runner_w.run_async(user_id="u1", session_id="w_sess", new_message=msg_w):
        if event.is_final_response():
            work_out = event.content.parts[0].text

    # --- STEP 2: EVALUATION ---
    yield "⚖️ **Step 2:** Evaluator Agent is auditing the response against the rubric..."
    
    await session_service.create_session(user_id="u1", session_id="e_sess", app_name=APP_NAME)
    runner_e = Runner(agent=evaluator, session_service=session_service, app_name=APP_NAME)
    
    eval_msg = (
        f"--- WORKER OUTPUT TO EVALUATE ---\n{work_out}\n"
        f"--- END OUTPUT ---\n"
        "Please provide the 1-5 scores and your reasoning."
    )
    
    score_report = ""
    msg_e = types.Content(role='user', parts=[types.Part(text=eval_msg)])
    async for event in runner_e.run_async(user_id="u1", session_id="e_sess", new_message=msg_e):
        if event.is_final_response():
            score_report = event.content.parts[0].text

    # --- FINAL OUTPUT ---
    yield "✅ Quality Audit complete."
    yield (
        f"### 🛠️ Primary Response\n{work_out}\n\n"
        f"--- \n"
        f"### ⭐ LLM-as-a-Judge Report\n{score_report}"
    )

# 4. Universal Entry Point
async def run_pattern(user_query: str):
    """Entry point for Streamlit dashboard."""
    return execute_evaluation(user_query)

if __name__ == "__main__":
    async def local_test():
        gen = await run_pattern("Explain how a nuclear reactor works.")
        async for update in gen:
            print(f"\n[Update]: {update}")
    
    asyncio.run(local_test())