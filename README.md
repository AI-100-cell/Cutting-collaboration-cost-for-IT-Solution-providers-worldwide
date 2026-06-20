IT Solution Multi-Agent 🤖

A multi-agent AI system built with LangGraph that automates collaboration
workflows for IT-solution providers — reducing the coordination cost of turning
client requirements into delivered solutions.


Final project for the Advanced Artificial Intelligence course at AtomCamp,
extended into a working multi-agent application.



What it does

Instead of one prompt-and-response chatbot, this uses multiple specialized agents
that hand work off to each other to complete a task end to end:


🧭 [Agent 1 — e.g. Sales] interprets the client request
🔍 [Agent 2 — e.g. Triage] gathers the information needed
🛠️ [Agent 3 — e.g. Iinside solution Architect] drafts the IT solution
✅ [Agent 4 — e.g. Team Lead] validates the output before delivery


Tech stack

LayerToolAgent orchestrationLangGraphLLMOpenAI (via langchain-openai)Data validationPydanticUIStreamlitConfigpython-dotenv

Architecture

Client request → [Sales] → [Triage] → [Solution Builder] → [Team Lead] → Output

<img width="3690" height="1750" alt="image" src="https://github.com/user-attachments/assets/f4b266d3-a5ce-4fba-9077-702dabc172a3" />


What I learned


Designing agent-to-agent handoffs and shared state in LangGraph
Keeping multi-agent output reliable with Pydantic schemas

https://screenrec.com/share/R7Fa1Skdej

