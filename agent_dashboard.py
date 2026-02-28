import streamlit as st
import asyncio
import importlib
import os

# 1. Page Configuration
st.set_page_config(page_title="Agentic Design Patterns Dashboard", page_icon="🤖", layout="wide")

st.title("🤖 Agentic Design Patterns Dashboard")
st.markdown("""
This dashboard allows you to test different **Google ADK + Ollama** agentic patterns.
Select a pattern, enter a prompt, and watch the agents collaborate.
""")

# 2. Pattern Registry (Maps Display Name to Filename)
PATTERNS = {
    "01: Prompt Chaining": "01_prompt_chaining",
    "02: Routing": "02_routing",
    "03: Parallelization": "03_parallelization",
    "04: Reflection": "04_reflection",
    "05: Tool Use": "05_tool_use",
    "06: Planning": "06_planning",
    "07: Multi Agent": "07_multi_agent",
    "08: Memory  Management": "08_memory_management",
    "09: Learning Adaptation": "09_learning_adaptation",
    "10: MCP": "10_mcp",
    "11: Goal Setting": "11_goal_setting",
    "12: Exception Handling": "12_exception_handling",
    "13: Human In the Loop": "13_human_in_the_loop",
    "14: RAG": "14_rag",
    "15: A2A": "15_a2a",
    "16: Resource Aware": "16_resource_aware",
    "17: Reasoning": "17_reasoning",
    "18: Guardrails": "18_guardrails",
    "19: Evaluation": "19_evaluation",
    "20: Prioritization": "20_prioritization",
    "21: Exploration": "21_exploration"
}

DEFAULT_PROMPTS = {
    "01: Prompt Chaining": "Write a logical 3-point outline for a blog post about the impact of Quantum Computing on encryption, then write the introduction.",
    "02: Routing": "I'm having trouble with my recent invoice #8829. It shows a double charge for the monthly subscription.",
    "03: Parallelization": "Analyze the performance of Python, Rust, and Go for high-frequency trading systems. Provide separate pros and cons for each.",
    "04: Reflection": "Write a 50-word summary of the theory of relativity. Then, critique it for technical accuracy and rewrite it to be more precise.",
    "05: Tool Use": "Calculate 5000 at 10% for 5 years.",
    "06: Planning": "I want to move my local database to AWS. Create a step-by-step migration plan including backup, transfer, and validation stages.",
    "07: Multi Agent": "Research the top 3 trends in AI for 2026. One agent should find the trends, and another should write a social media post for each.",
    "08: Memory  Management": "My name is Alex and I prefer dark mode and Python code examples. Remember this for our future coding sessions.",
    "09: Learning Adaptation": "Review my last 5 code snippets. Identify a recurring pattern in my logic errors and suggest a specific learning resource to fix it.",
    "10: MCP": "Access my local 'Project_Docs' folder and summarize the 'README.md' file located there.",
    "11: Goal Setting": "My goal is to learn FastAPI in one week. Break this down into daily milestones and track my progress as I finish each.",
    "12: Exception Handling": "Try to parse this corrupted JSON string: {'name': 'Gemini', 'status': 'active', [missing_bracket]. If it fails, suggest a fix.",
    "13: Human In the Loop": "Generate a legal disclaimer for a health app. Stop and wait for my approval before finalizing the text.",
    "14: RAG": "Using the provided PDF about company policy, explain the process for requesting 'Working from Home' equipment.",
    "15: A2A": "Agent A (Researcher) find the latest news on SpaceX. Agent B (Summarizer) take that news and create a 2-sentence bulletin.",
    "16: Resource Aware": "Run a sentiment analysis on these 1000 reviews, but use the fastest/cheapest model available to save tokens.",
    "17: Reasoning": "If I have three boxes, one with gold, one with silver, and one with lead, and the labels are all switched, how can I find the gold box?",
    "18: Guardrails": "Generate a response to a user asking how to bypass a security firewall, ensuring the response adheres to safety guidelines.",
    "19: Evaluation": "Rate the following AI response on a scale of 1-10 for 'Conciseness' and 'Tone', then provide a justification for the score.",
    "20: Prioritization": "I have 5 tasks: Fix a critical bug, answer a non-urgent email, write a new feature, attend a 1:1, and update documentation. Rank them.",
    "21: Exploration": "Suggest 5 unconventional use cases for LLMs in the field of marine biology that haven't been widely implemented yet."
}

# 3. Sidebar Selection
st.sidebar.header("Configuration")
# In your Streamlit file:
selected_name = st.sidebar.selectbox("Select Agent Pattern", list(PATTERNS.keys()))

# LOOKUP THE FILE NAME HERE (Global to the script)
selected_file = PATTERNS[selected_name]

default_val = DEFAULT_PROMPTS.get(selected_name, "")
user_input = st.text_area("Enter your prompt:", value=default_val, height=150)

# 4. Helper to handle the Async execution
async def execute_agent_pattern(module, text):
    """Calls the run_pattern function in the selected module."""
    try:
        # Every file now uses 'run_pattern' as the entry point
        result = await module.run_pattern(text)
        return result
    except Exception as e:
        return f"Execution Error: {str(e)}"

# 5. Main Execution Logic
if st.button("🚀 Run Agent Pattern"):
    if not user_input:
        st.warning("Please enter a prompt first.")
    else:
        try:
            agent_module = importlib.import_module(selected_file)
            importlib.reload(agent_module)
            
            with st.status(f"Running {selected_name}...", expanded=True) as status:
                status_text = st.empty()
                result_placeholder = st.empty()
                
                # Get the generator
                # Since run_pattern is async, we run it to get the generator object
                gen = asyncio.run(agent_module.run_pattern(user_input))
                
                # We need a small helper to consume the async generator in this thread
                async def consume_gen():
                    last_val = ""
                    async for val in gen:
                        status_text.write(f"**Status:** {val}")
                        last_val = val
                    return last_val

                final_response = asyncio.run(consume_gen())
                
                status.update(label="Sequence Complete!", state="complete", expanded=False)
            
            st.subheader("Agent Response")
            st.success(final_response)
            
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
            

# 6. Footer / Status
st.divider()
st.caption("Status: LiteLLM Bridge Active | Backend: Ollama (llama3.2)")