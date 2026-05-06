# shared/state.py
# This is the shared ticket that all agents read and update.

# shared/state.py
  # The shared ticket that travels Sales → Triage → Inside Solution
  # NOW INCLUDES: chat_log for live messages, triage_pending flag
  
from typing import Optional, List
from pydantic import BaseModel, Field
class ChatMessage(BaseModel):
      sender: str = ''        # e.g. 'Sales', 'Triage', 'Ahmed Khan'
      role:   str = ''        # 'sales' | 'triage' | 'specialist' | 'team_lead'
      text:   str = ''        # the message content
      time:   str = ''        # timestamp string
  
class SolutionTicket(BaseModel):
      # Filled by Sales Agent
      customer_name:    str = ''
      customer_request: str = ''
      from_team:        str = 'sales'
  
      # Filled by Triage Agent (manually via UI buttons)
      solution_type:    str = ''
      assigned_to:      str = ''
      priority:         str = 'normal'
  
      # Filled by Inside Solution Agent
      solution_details: str = ''
      estimated_cost:   str = ''
      timeline:         str = ''
  
      # Status
      status: str = 'new'   # new → pending_triage → triaged → in_progress → won
      notes:  str = ''
  
      # NEW — Live chat log visible to all teams
      chat_log: List[ChatMessage] = Field(default_factory=list)
  
      # NEW — True means Triage has not yet assigned this ticket
      triage_pending: bool = True
