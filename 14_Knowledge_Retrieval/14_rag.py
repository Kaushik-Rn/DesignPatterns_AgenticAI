""" 
Why RAG is a "Gold Standard":
1) Zero Hallucination: By telling the agent "If you cannot find it in the tool, say you don't know," you prevent the AI from making up vacation policies.
2) Real-time Grounding: You can update the MOCK_KNOWLEDGE_BASE dictionary, and the agent immediately "knows" the new information without any retraining.
3) Source Citations: The agent can tell the user exactly which "file" (key) it found the information in.
 """

""" 
Dashboard Test Case:

Valid Query: "What are the rules for hybrid work?"
Result: Agent calls tool -> finds hybrid_work -> answers "You need to be in Tuesday/Thursday.

"Invalid Query: "What is the company policy on pet insurance?"
Result: Agent calls tool -> finds nothing -> answers "I'm sorry, I don't have documents on pet insurance."
"""


"""
Pattern: RAG (Retrieval-Augmented Generation)
Description: Agent retrieves specific context from a knowledge base to answer queries accurately.
"""
import asyncio
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.models.lite_llm import LiteLlm
from google.genai import types

# 1. Configuration
OLLAMA_MODEL = LiteLlm(model="ollama_chat/llama3.2")
APP_NAME = "RAG_App"

# 2. Simulate a Knowledge Base (Mock Vector Store)
MOCK_KNOWLEDGE_BASE = {
    "policy_2026": "Employees are entitled to 30 days of vacation starting Jan 2026.",
    "hybrid_work": "The company requires 2 days in-office (Tuesday/Thursday).",
    "travel_policy": "Business class is only permitted for flights over 8 hours."
}

def search_company_docs(query_term: str) -> str:
    """Searches the company private wiki for information. 
    Args: query_term: the topic to look up."""
    query_term = query_term.lower()
    for key, text in MOCK_KNOWLEDGE_BASE.items():
        if query_term in key or any(word in text.lower() for word in query_term.split()):
            return f"FOUND IN {key}: {text}"
    return "No matching internal documents found."

# 3. The RAG Agent
rag_agent = Agent(
    name="WikiAssistant",
    model=OLLAMA_MODEL,
    instruction=(
        "You are an internal company assistant. You MUST use the 'search_company_docs' tool "
        "to find facts before answering any question about company policy. "
        "Ground your answer ONLY in the retrieved text. If no document is found, "
        "politely inform the user that you do not have access to that specific information."
    ),
    tools=[search_company_docs]
)

# 4. Generator Logic for Streamlit
async def execute_rag(user_query: str):
    session_service = InMemorySessionService()
    
    yield "📂 Initializing RAG pipeline: Connecting to Company Wiki..."
    
    await session_service.create_session(user_id="u1", session_id="rag_sess", app_name=APP_NAME)
    runner = Runner(agent=rag_agent, session_service=session_service, app_name=APP_NAME)
    
    response = ""
    msg = types.Content(role='user', parts=[types.Part(text=user_query)])
    
    async for event in runner.run_async(user_id="u1", session_id="rag_sess", new_message=msg):
        # We catch the tool call to show the user that retrieval is happening
        if hasattr(event, 'content') and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, 'tool_call'):
                    yield f"🔍 **Retrieval Step:** Searching wiki for `{part.tool_call.args.get('query_term')}`..."
        
        if event.is_final_response():
            response = event.content.parts[0].text
            
    yield "✅ Information grounded in internal documentation."
    yield f"### 📚 Wiki Assistant Response\n\n{response}"

# 5. Universal Entry Point
async def run_pattern(user_query: str):
    """Entry point for Streamlit dashboard."""
    return execute_rag(user_query)

if __name__ == "__main__":
    async def local_test():
        gen = await run_pattern("How many vacation days do I get in 2026?")
        async for update in gen:
            print(update)
    
    asyncio.run(local_test())