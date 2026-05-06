# agents/sales_agent.py
# Sales Agent — receives customer request and creates a ticket.
# Replaces: Outlook (no email license needed)

import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from shared.state import SolutionTicket

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def run_sales_agent(customer_name: str, customer_request: str) -> SolutionTicket:
    """
    Sales team receives a customer request.
    The LLM reads it and fills in the basic ticket details.
    """

    print(f"\n[Sales Agent] New request from: {customer_name}")
    print(f"[Sales Agent] Request: {customer_request}")

    # Ask the LLM to understand the request
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",   # free-tier friendly model
        messages=[
            {
                "role": "system",
                "content": """You are a Sales Agent at an IT solutions company.
                A customer has sent a request. Read it and extract:
                - What IT product/solution they need
                - How urgent it is (low/normal/high)
                - A short summary of what they want
                
                Reply in this exact JSON format:
                {
                  "product_hint": "e.g. VMware, Dell Server, Networking, Cloud, HPE, APC, Lenovo, Digital Workplace",
                  "priority": "low or normal or high",
                  "summary": "one sentence summary"
                }
                Only reply with JSON. Nothing else."""
            },
            {
                "role": "user",
                "content": customer_request
            }
        ]
    )

    # Parse LLM response
    raw = response.choices[0].message.content.strip()

    try:
        data = json.loads(raw)
    except:
        # If LLM gives messy output, use safe defaults
        data = {"product_hint": "General IT", "priority": "normal", "summary": customer_request}

    # Build the ticket
    ticket = SolutionTicket(
        from_team="sales",
        customer_name=customer_name,
        customer_request=customer_request,
        solution_type=data.get("product_hint", "Unknown"),
        priority=data.get("priority", "normal"),
        notes=data.get("summary", ""),
        status="new"
    )

    print(f"[Sales Agent] Ticket created — Type: {ticket.solution_type} | Priority: {ticket.priority}")
    return ticket


# ── Quick test — run this file directly to test Sales Agent ──────
if __name__ == "__main__":
    ticket = run_sales_agent(
        customer_name="Zara Technologies",
        customer_request="We need to virtualise our 20 physical servers. We are considering VMware vSphere. Can you provide a quote and implementation plan?"
    )
    print("\n── Ticket Created ──")
    print(ticket.model_dump_json(indent=2))