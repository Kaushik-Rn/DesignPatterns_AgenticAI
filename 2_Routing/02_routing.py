# Sample Prompts:
# Need details on invoices
# Need technical help
# Based on above prompts, the execution is routed to right agent


"""
Pattern: Routing (The Dispatcher)
Description: Classifies user intent and routes to a specialized sub-agent.
"""
import asyncio
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.models.lite_llm import LiteLlm
from google.genai import types

# 1. Configuration
OLLAMA_MODEL = LiteLlm(model="ollama_chat/llama3.2")
APP_NAME = "RoutingApp"

# 2. Define Specialized Agents
billing_agent = Agent(
    name="BillingSpecialist",
    model=OLLAMA_MODEL,
    instruction=(
        "You are a Billing Specialist. Answer queries about invoices, "
        "refunds, and payments. Always be professional and offer to "
        "escalate to a human if you can't find a record."
    )
)

tech_support_agent = Agent(
    name="TechSupportSpecialist",
    model=OLLAMA_MODEL,
    instruction=(
        "You are a Technical Support Engineer. Help users with software "
        "bugs, installation errors, and login issues. Be technical but clear."
    )
)

# 3. Universal Entry Point (Generator for Streamlit)
async def execute_routing(user_query: str):
    """
    Logic moved here to support yielding status updates to the dashboard.
    """
    session_service = InMemorySessionService()
    query_lower = user_query.lower()
    
    # --- Step 1: Classification ---
    yield "🔍 Analyzing intent and selecting agent..."
    
    if any(k in query_lower for k in ["bill", "pay", "refund", "invoice", "price"]):
        target_agent = billing_agent
        agent_type = "Billing"
    elif any(k in query_lower for k in ["bug", "error", "login", "broken", "install"]):
        target_agent = tech_support_agent
        agent_type = "Tech Support"
    else:
        target_agent = tech_support_agent
        agent_type = "Tech Support (Default)"

    yield f"🚦 Routed to: **{target_agent.name}** ({agent_type})"

    # --- Step 2: Execution ---
    await session_service.create_session(
        user_id="u1", 
        session_id="route_sess", 
        app_name=APP_NAME
    )
    
    runner = Runner(
        agent=target_agent, 
        session_service=session_service, 
        app_name=APP_NAME
    )
    
    msg = types.Content(role='user', parts=[types.Part(text=user_query)])
    
    response_text = ""
    async for event in runner.run_async(user_id="u1", session_id="route_sess", new_message=msg):
        if event.is_final_response():
            response_text = event.content.parts[0].text
            
    # Final yield is the response displayed in the success box
    yield f"**[{target_agent.name} Response]**\n\n{response_text}"

async def run_pattern(user_query: str):
    """Entry point for Streamlit dashboard."""
    return execute_routing(user_query)

if __name__ == "__main__":
    # To run locally via terminal, you'd need to consume the generator:
    async def local_test():
        gen = await run_pattern("My invoice is wrong")
        async for update in gen:
            print(update)
    
    asyncio.run(local_test())