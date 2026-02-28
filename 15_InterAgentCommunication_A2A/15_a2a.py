""" 
Why A2A is powerful for your Dashboard:

1) Recursive Problem Solving: The Coordinator doesn't need to know how to write poetry or speak French; it just needs to know which "Expert Agent" to call.
2) Encapsulation: If you want to change the "Poet" from a 4-line specialist to a Haiku specialist, you only change the poet_agent definition. The rest of the network continues to work perfectly.
3) Visual Handshakes: In the Streamlit UI, the user will see the "A2A Handshake" status, making it clear that multiple "minds" are working together on their request.
 """

""" 
Dashboard Test Case:
Prompt: "Write a poem about the moon in French."
Expected Behavior: The dashboard will show two separate handshakes—one for the Poet to get the English lines, 
and another for the Translator to convert them.
"""

"""
Pattern: A2A Communication (The Network)
Description: Agents invoke one another as specialized tools, enabling a flat, collaborative network.
"""
import asyncio
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.models.lite_llm import LiteLlm
from google.genai import types

# 1. Configuration
OLLAMA_MODEL = LiteLlm(model="ollama_chat/llama3.2")
APP_NAME = "A2A_Network"

# 2. Define Peer Agents (These act as services)
translator_agent = Agent(
    name="Translator",
    model=OLLAMA_MODEL,
    instruction="Translate the provided text into French. Return ONLY the translated text."
)

poet_agent = Agent(
    name="Poet",
    model=OLLAMA_MODEL,
    instruction="Write a short, 4-line poem about the user's topic. Be expressive."
)

# 3. Define the Global Coordinator
# We pass the other agents INTO the tools list.
network_orchestrator = Agent(
    name="GlobalCoordinator",
    model=OLLAMA_MODEL,
    instruction=(
        "You are a network coordinator. To fulfill requests: "
        "1. Use 'Poet' to generate creative content. "
        "2. Use 'Translator' to handle language conversion. "
        "Always present the original English poem followed by the French translation."
    ),
    tools=[translator_agent, poet_agent]
)

# 4. Generator Logic for Streamlit
async def execute_a2a(user_query: str):
    session_service = InMemorySessionService()
    SID = "a2a_sess"
    
    yield "🌐 Initializing Peer-to-Peer Agent Network..."
    await session_service.create_session(user_id="u1", session_id=SID, app_name=APP_NAME)
    
    runner = Runner(agent=network_orchestrator, session_service=session_service, app_name=APP_NAME)
    msg = types.Content(role='user', parts=[types.Part(text=user_query)])
    
    final_response = ""
    async for event in runner.run_async(user_id="u1