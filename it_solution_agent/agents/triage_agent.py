# agents/triage_agent.py
import streamlit as st
import os, json, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from openai import OpenAI
from dotenv import load_dotenv
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.state import SolutionTicket, ChatMessage
from datetime import datetime

load_dotenv()

client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
    timeout=30
)

# Team mapping
  # Solution categories Triage can choose from
SOLUTION_TYPES = [
      'VMware', 'Dell Server', 'Lenovo Server', 'HPE Server',
      'APC', 'Networking', 'Cloud', 'Digital Workplace'
      # NOTE: General IT and Team Lead are REMOVED
      # Team Lead is monitor only — never assigned a customer request
  ]
  
  # Team members per solution — Triage can override this in the UI
TEAM_MEMBERS = {
      'VMware':            'Kashif Ali (VMware Specialist)',
      'Dell Server':       'Adil Baig (Dell & Hardware Lead)',
      'Lenovo Server':     'Danish Shaukat (Lenovo Hardware Lead)',
      'HPE Server':        'Usama Ali (HPE Engineer)',
      'APC':               'Josie Gardwohl (HPE Engineer)',
      'Networking':        'Muaaz Nawaz (Network Engineer)',
      'Cloud':             'Muhammad Ateeb (Cloud Architect)',
      'Digital Workplace': 'Zaid Saleem (Workplace Solutions)',
  }
  
  # All assignable specialists (shown in Triage dropdown)
ALL_SPECIALISTS = list(set(TEAM_MEMBERS.values()))


# Fallback keyword classifier (VERY IMPORTANT)
def keyword_classify(text):
    text = text.lower()

    if "vmware" in text:
        return "VMware"
    elif "dell" in text or "poweredge" in text:
        return "Dell Server"
    elif "lenovo" in text:
        return "Lenovo Server"
    elif "hpe" in text:
        return "HPE Server"
    elif "apc" in text or "ups" in text:
        return "APC"
    elif "network" in text or "switch" in text or "firewall" in text or "cisco" in text:
        return "Networking"
    elif "cloud" in text or "aws" in text or "azure" in text:
        return "Cloud"
    elif "laptop" in text or "workplace" in text:
        return "Digital Workplace"

    return "General IT"


def run_triage_agent_nlp(ticket: SolutionTicket) -> SolutionTicket:
      '''
      Step 1 — NLP only: LLM suggests a solution type.
      Triage can accept or override this suggestion in the UI.
      This does NOT assign anyone — Triage does that manually.
      '''
      print(f'[Triage] NLP classifying: {ticket.customer_name}')
  
      response = client.chat.completions.create(
          model='gpt-3.5-turbo',
          messages=[
              {'role': 'system', 'content': '''
               Classify into exactly ONE:
               VMware | Dell Server | Lenovo Server | HPE Server |
               APC | Networking | Cloud | Digital Workplace
               DO NOT use General IT or Team Lead.
               Reply only in JSON: {"type": "category", "reason": "one sentence"}
               Only JSON. Nothing else.'''},
              {'role': 'user', 'content': f'Request: {ticket.customer_request}'}
          ]
      )
      try:
          data = json.loads(response.choices[0].message.content.strip())
      except:
          data = {'type': 'General IT', 'reason': 'Could not classify'}
  
      # Store the NLP suggestion — Triage will confirm or override in UI
      ticket.solution_type   = data.get('type', 'General IT')
      ticket.triage_pending  = True   # still waiting for human Triage confirmation
      ticket.status          = 'pending_triage'
      ticket.notes          += f' | NLP suggestion: {data.get("reason", "")}'
  
      print(f'[Triage] NLP suggests: {ticket.solution_type} — waiting for Triage to confirm')
      return ticket
  
  
def confirm_triage_assignment(ticket: SolutionTicket,
                                solution_type: str,
                                assigned_to: str) -> SolutionTicket:
      '''
      Step 2 — Called when Triage clicks CONFIRM in the UI.
      Triage has chosen the solution type and the specialist.
      Posts assignment message to the live chat.
      '''
      ticket.solution_type  = solution_type
      ticket.assigned_to    = assigned_to
      ticket.status         = 'triaged'
      ticket.triage_pending = False
  
      # Post assignment to live chat — everyone sees this
      ticket.chat_log.append(ChatMessage(
          sender = 'Triage Team',
          role   = 'triage',
          text   = f'🔀 ASSIGNED: {ticket.customer_name} [{solution_type}] → {assigned_to}  |  Priority: {ticket.priority}',
          time   = datetime.now().strftime('%H:%M:%S')
      ))
  
      print(f'[Triage] Assignment confirmed: {assigned_to} → {solution_type}')
      return ticket
