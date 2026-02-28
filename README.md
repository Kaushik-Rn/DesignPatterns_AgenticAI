
# 🤖 Google ADK Agentic Design Patterns
A complete implementation of 21 Agentic Design Patterns using the **Google Agent Development Kit (ADK)** and **Ollama (Llama 3.2)**.

## Quick Start
1. **Install Ollama**: Download and run Ollama, then pull the model:
   ```bash
   ollama pull llama3.2

2. **Install Dependencies**:
pip install -r requirements.txt

3. **Launch the Dashboard**:
streamlit run agent_dashboard.py

**Project Structure**:
1. agent_dashboard.py: The main UI to test all patterns.
2. 01_prompt_chaining.py ... 21_exploration.py: Individual pattern implementations.
3. All patterns follow a universal run_pattern(user_query) interface for dynamic execution.

**The 21 Patterns**:
ID          Pattern                          Use Case
01-04     Workflows             "Chaining, Routing, Parallel, Reflection"
05-08     Capabilities          "Tools, Planning, Orchestration, Memory"
09-12     Production            "Learning, MCP, Monitoring, Exception Handling"
13-16     Enterprise            "HITL, RAG, A2A, Resource Awareness"
17-21     Advanced              "Reasoning, Guardrails, Eval, Priority, Exploration"

**Implementation Note**:
Each pattern uses LiteLLM as the model bridge and InMemorySessionService for state management. 
For production use, consider migrating to a database-backed session service
