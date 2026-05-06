import os, json, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from openai import OpenAI
from dotenv import load_dotenv
from shared.state import SolutionTicket, ChatMessage
from datetime import datetime

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


def run_inside_solution_agent(ticket: SolutionTicket):
    print(f'[Solution] Building proposal for: {ticket.customer_name}')
    print(f'[Solution] Specialist: {ticket.assigned_to}')

    # --- LLM or fallback ---
    if os.getenv('OPENAI_API_KEY') == 'your_actual_openai_api_key_here':
        data = {
            'details': 'Custom solution',
            'cost': 'TBD',
            'timeline': '2-4 weeks',
            'pitch': 'We deliver quality.'
        }
    else:
        try:
            response = client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[
                    {
                        'role': 'system',
                        'content': f'''You are {ticket.assigned_to} at an IT company.
Build a proposal. Reply ONLY in JSON:

{{
  "details": "2-3 bullet points",
  "cost": "USD range e.g. $10,000-$15,000",
  "timeline": "e.g. 3-4 weeks",
  "pitch": "one sentence"
}}'''
                    },
                    {
                        'role': 'user',
                        'content': f'''Customer: {ticket.customer_name}
Solution: {ticket.solution_type}
Request: {ticket.customer_request}'''
                    }
                ]
            )

            raw = response.choices[0].message.content.strip()

            try:
                data = json.loads(raw)
            except:
                data = {
                    'details': 'Custom solution',
                    'cost': 'TBD',
                    'timeline': '2-4 weeks',
                    'pitch': 'We deliver quality.'
                }

        except Exception as e:
            print(f'[Solution Agent] LLM error: {e}')
            data = {
                'details': 'Custom solution',
                'cost': 'TBD',
                'timeline': '2-4 weeks',
                'pitch': 'We deliver quality.'
            }

    # --- Update ticket ---
    ticket.solution_details = data.get('details', '')
    ticket.estimated_cost   = data.get('cost', '')
    ticket.timeline         = data.get('timeline', '')
    ticket.status           = 'in_progress'
    ticket.notes           += f' | Pitch: {data.get("pitch", "")}'

    # --- Safe formatting ---
    cost = ticket.estimated_cost or "TBD"
    timeline = ticket.timeline or "TBD"

    # --- Append chat message ---
    ticket.chat_log.append(ChatMessage(
        sender=ticket.assigned_to or "system",
        role='specialist',
        text=(
            f'✅ ACKNOWLEDGED — I have received the {ticket.solution_type} request '
            f'from {ticket.customer_name}. Working on proposal. '
            f'Estimated cost: {cost} | Timeline: {timeline}'
        ),
        time=datetime.utcnow().isoformat()
    ))

    print_solution_details(ticket)

    return ticket


def print_solution_details(ticket):
    print(f'[Inside Solution Agent] Solution built!')
    print(f'[Inside Solution Agent] Cost     : {ticket.estimated_cost}')
    print(f'[Inside Solution Agent] Timeline : {ticket.timeline}')
    print(f'[Inside Solution Agent] Status   : {ticket.status}')
