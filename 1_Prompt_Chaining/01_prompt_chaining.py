"""
Pattern: Prompt Chaining
Description: Sequential task execution using local Ollama llama3.2.
"""
import asyncio
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.models.lite_llm import LiteLlm  # <--- IMPORT THIS
from google.genai import types

import nest_asyncio
nest_asyncio.apply()

# 1. Define the Model using the 'ollama_chat/' prefix
# This specifically tells the ADK to use the LiteLLM Chat bridge.
OLLAMA_MODEL = LiteLlm(model="ollama_chat/llama3.2")

# 2. Define the Agents
outline_agent = Agent(
    name="OutlineAgent",
    model=OLLAMA_MODEL,
    instruction="Create a logical 3-point outline for a blog post on the given topic."
)

writer_agent = Agent(
    name="WriterAgent",
    model=OLLAMA_MODEL,
    instruction="Write a 150-word intro paragraph based on the provided outline."
)


async def execute_chain(topic: str):
    session_service = InMemorySessionService()
    APP_NAME = "ChainDemoApp"
    
    # --- Step 1: Outline ---
    yield "🔄 Generating logical 3-point outline..."
    await session_service.create_session(user_id="u1", session_id="s1", app_name=APP_NAME)
    runner1 = Runner(agent=outline_agent, session_service=session_service, app_name=APP_NAME)
    
    outline_text = ""
    msg1 = types.Content(role='user', parts=[types.Part(text=topic)])
    async for event in runner1.run_async(user_id="u1", session_id="s1", new_message=msg1):
        if event.is_final_response():
            outline_text = event.content.parts[0].text

    # --- Step 2: Writer ---
    yield "📝 Writing intro paragraph based on outline..."
    await session_service.create_session(user_id="u1", session_id="s2", app_name=APP_NAME)
    runner2 = Runner(agent=writer_agent, session_service=session_service, app_name=APP_NAME)
    
    msg2 = types.Content(role='user', parts=[types.Part(text=f"Outline: {outline_text}")])
    final_text = ""
    async for event in runner2.run_async(user_id="u1", session_id="s2", new_message=msg2):
        if event.is_final_response():
            final_text = event.content.parts[0].text
            
    yield final_text # Final yield is the result

async def run_pattern(topic: str):
    # This now returns a generator
    return execute_chain(topic)

    
if __name__ == "__main__":
    run_pattern("The Future of AI")