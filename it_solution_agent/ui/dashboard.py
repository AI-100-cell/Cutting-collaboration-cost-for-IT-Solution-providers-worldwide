  # ui/dashboard.py
  # FULL REWRITE — 4-tab dashboard
  # Tab 1 — Sales: submit customer request
  # Tab 2 — Triage: see requests, assign manually with buttons
  # Tab 3 — Specialist: see assignment, click Acknowledge
  # Tab 4 — Team Lead: full activity monitor (view only)
  # Add a simple password to limit who can use it

import streamlit as st
st.title("AI Sales Dashboard")
# Add a simple password to limit who can use it
password = st.text_input("Enter demo password", type="password")
if password != "atomcamp2026":
    st.warning("Enter the password to use this dashboard.")
    st.stop()
st.write("System is running 🚀")
import sys, os, json
from datetime import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
  
from shared.state import SolutionTicket, ChatMessage
from agents.sales_agent import run_sales_agent
from agents.triage_agent import (
      run_triage_agent_nlp,
      confirm_triage_assignment,
      SOLUTION_TYPES,
      TEAM_MEMBERS,
      ALL_SPECIALISTS,
  )
from agents.inside_solution_agent import run_inside_solution_agent
  
  # ── Page config ───────────────────────────────────────
st.set_page_config(
      page_title='IT Solution Agent — Atomcamp',
      page_icon='🤖',
      layout='wide'
  )
  
  # ── Session state — shared memory across all tabs ─────
  # This keeps the ticket alive while you switch tabs
if 'ticket' not in st.session_state:
      st.session_state.ticket = None
if 'chat_log' not in st.session_state:
      st.session_state.chat_log = []
if 'pipeline_stage' not in st.session_state:
      st.session_state.pipeline_stage = 'waiting_sales'
      # Stages: waiting_sales → pending_triage → triaged → in_progress
  
  # ── Header ────────────────────────────────────────────
st.title('🤖 IT Solution Multi-Agent System')
st.caption('Atomcamp Institute — Final Project')
  
  # ── Live chat sidebar — visible to ALL tabs ───────────
with st.sidebar:
      st.header('💬 Live Team Chat')
      st.caption('All teams see this in real time')
      st.divider()
      if st.session_state.chat_log:
          for msg in st.session_state.chat_log:
              # Colour code by role
              if msg['role'] == 'sales':
                  st.info(f"🟢 **{msg['sender']}** [{msg['time']}]\n{msg['text']}")
              elif msg['role'] == 'triage':
                  st.warning(f"🟡 **{msg['sender']}** [{msg['time']}]\n{msg['text']}")
              elif msg['role'] == 'specialist':
                  st.success(f"🔵 **{msg['sender']}** [{msg['time']}]\n{msg['text']}")
              elif msg['role'] == 'team_lead':
                  st.error(f"🟣 **{msg['sender']}** [{msg['time']}]\n{msg['text']}")
      else:
          st.caption('No messages yet. Sales team submits a request to start.')
      st.divider()
      st.caption('👥 Team: Ahmed · Sara · Bilal · Omar · Fatima · Zaid')
  
  # ── 4 Tabs ────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
      '📧 Sales Team',
      '🔀 Triage Team',
      '🛠️ Specialist',
      '👁️ Team Lead Monitor'
  ])
  
  # ══════════════════════════════════════════════════════
  # TAB 1 — SALES TEAM
  # ══════════════════════════════════════════════════════
with tab1:
      st.subheader('📧 Sales Team — Submit Customer Request')
      st.info('Sales team fills in the customer request here and submits it to Triage.')
  
      with st.form('sales_form'):
          customer_name = st.text_input(
              'Customer / Company Name',
              placeholder='e.g. Zara Technologies'
          )
          customer_request = st.text_area(
              'Customer Requirement',
              placeholder='Describe what the customer needs in detail...',
              height=140
          )
          priority = st.selectbox('Priority', ['normal', 'high', 'low'])
          submitted = st.form_submit_button(
              '📤 Submit to Triage',
              use_container_width=True,
              type='primary'
          )
  
      if submitted:
          if not customer_name or not customer_request:
              st.warning('Please fill in both the company name and the requirement.')
          else:
              with st.spinner('Sales Agent processing request...'):
                  ticket = run_sales_agent(customer_name, customer_request)
                  ticket.priority = priority
                  # Run NLP on triage side immediately (suggestion only)
                  ticket = run_triage_agent_nlp(ticket)
                  # Save to session state
                  st.session_state.ticket = ticket.model_dump()
                  st.session_state.chat_log = [m.model_dump() for m in ticket.chat_log]
                  st.session_state.pipeline_stage = 'pending_triage'
              st.success('✅ Request submitted! Go to the Triage Team tab to assign it.')
              st.balloons()
  
      # Show current ticket status if exists
      if st.session_state.ticket:
          st.divider()
          st.subheader('📋 Current Ticket Status')
          t = st.session_state.ticket
          col1, col2, col3 = st.columns(3)
          with col1: st.metric('Customer', t.get('customer_name','—'))
          with col2: st.metric('Status', t.get('status','—').upper())
          with col3: st.metric('Assigned To', t.get('assigned_to','Waiting for Triage...'))
  
  # ══════════════════════════════════════════════════════
  # TAB 2 — TRIAGE TEAM
  # ══════════════════════════════════════════════════════
with tab2:
      st.subheader('🔀 Triage Team — Review and Assign')
      st.info('Triage team reviews each request, chooses the solution type and assigns the right specialist. Team Lead is never assigned a customer request.')
  
      if not st.session_state.ticket:
          st.warning('⏳ No request from Sales team yet. Wait for Sales to submit a request.')
      elif st.session_state.pipeline_stage == 'triaged':
          t = st.session_state.ticket
          st.success(f'✅ Already assigned: {t.get("assigned_to")} → {t.get("solution_type")}')
      else:
          t = st.session_state.ticket
          st.divider()
  
          # Show what Sales sent
          st.subheader('📥 Request from Sales Team')
          col1, col2 = st.columns(2)
          with col1:
              st.markdown(f'**Customer:** {t.get("customer_name")}')
              st.markdown(f'**Priority:** {t.get("priority","normal").upper()}')
          with col2:
              st.markdown(f'**NLP Suggestion:** {t.get("solution_type","Unknown")}')
              st.caption('(You can accept this or choose a different type below)')
          st.text_area(
              'Customer Requirement',
              value=t.get('customer_request',''),
              height=100,
              disabled=True
          )
  
          st.divider()
          st.subheader('🎛️ Triage Controls — Manual Assignment')
  
          col1, col2 = st.columns(2)
          with col1:
              # Dropdown to choose solution type
              # Pre-select NLP suggestion if it matches
              nlp_suggestion = t.get('solution_type', SOLUTION_TYPES[0])
              default_idx = SOLUTION_TYPES.index(nlp_suggestion) if nlp_suggestion in SOLUTION_TYPES else 0
              chosen_solution = st.selectbox(
                  '📦 Solution Type',
                  SOLUTION_TYPES,
                  index=default_idx,
                  help='Choose the IT solution category for this request'
              )
  
          with col2:
              # When solution type changes, suggest the right specialist
              default_specialist = TEAM_MEMBERS.get(chosen_solution, ALL_SPECIALISTS[0])
              specialist_idx = ALL_SPECIALISTS.index(default_specialist) if default_specialist in ALL_SPECIALISTS else 0
              chosen_specialist = st.selectbox(
                  '👤 Assign To',
                  ALL_SPECIALISTS,
                  index=specialist_idx,
                  help='Choose which specialist gets this request'
              )
  
          # Priority override
          new_priority = st.select_slider(
              '🚦 Priority',
              options=['low', 'normal', 'high'],
              value=t.get('priority', 'normal')
          )
  
          # Triage notes
          triage_note = st.text_input(
              '📝 Triage Note (optional)',
              placeholder='e.g. Customer is a key account — fast turnaround needed'
          )
  
          st.divider()
          # CONFIRM button
          if st.button('✅ Confirm Assignment', type='primary', use_container_width=True):
              with st.spinner('Confirming assignment...'):
                  ticket_obj = SolutionTicket(**st.session_state.ticket)
                  # Restore existing chat log
                  from shared.state import ChatMessage
                  ticket_obj.chat_log = [ChatMessage(**m) for m in st.session_state.chat_log]
                  ticket_obj.priority = new_priority
                  if triage_note:
                      ticket_obj.notes += f' | Triage note: {triage_note}'
                  # Confirm the manual assignment
                  ticket_obj = confirm_triage_assignment(
                      ticket_obj, chosen_solution, chosen_specialist
                  )
                  # Team Lead monitoring log
                  ticket_obj.chat_log.append(ChatMessage(
                      sender='Team Lead Monitor',
                      role='team_lead',
                      text=f'👁️ MONITORED: Triage assigned {chosen_specialist} to {ticket_obj.customer_name} [{chosen_solution}]',
                      time=datetime.now().strftime('%H:%M:%S')
                  ))
                  st.session_state.ticket = ticket_obj.model_dump()
                  st.session_state.chat_log = [m.model_dump() for m in ticket_obj.chat_log]
                  st.session_state.pipeline_stage = 'triaged'
              st.success(f'✅ Assigned {chosen_specialist} to handle {chosen_solution} for {t.get("customer_name")}')
              st.rerun()
  
  # ══════════════════════════════════════════════════════
  # TAB 3 — SPECIALIST
  # ══════════════════════════════════════════════════════
with tab3:
      st.subheader('🛠️ Specialist — Acknowledge and Build Proposal')
  
      if not st.session_state.ticket:
          st.warning('⏳ No assignment yet. Triage team needs to assign a request first.')
      elif st.session_state.pipeline_stage == 'pending_triage':
          st.warning('⏳ Triage team is reviewing the request. Please wait for assignment.')
      elif st.session_state.pipeline_stage in ['triaged', 'in_progress']:
          t = st.session_state.ticket
          st.info(f'You have been assigned a new task by Triage.')
  
          col1, col2, col3 = st.columns(3)
          with col1: st.metric('Customer',      t.get('customer_name'))
          with col2: st.metric('Solution Type', t.get('solution_type'))
          with col3: st.metric('Assigned To',   t.get('assigned_to'))
  
          st.divider()
          st.subheader('📋 Customer Requirement')
          st.text_area('',value=t.get('customer_request',''),height=100,disabled=True)
  
          if st.session_state.pipeline_stage == 'triaged':
              st.divider()
              st.subheader('👆 Click to Acknowledge Assignment')
              if st.button(
                  f'✅ I Accept — Start Building Proposal',
                  type='primary',
                  use_container_width=True
              ):
                  with st.spinner('Building solution proposal...'):
                      ticket_obj = SolutionTicket(**st.session_state.ticket)
                      from shared.state import ChatMessage
                      ticket_obj.chat_log = [ChatMessage(**m) for m in st.session_state.chat_log]
                      ticket_obj = run_inside_solution_agent(ticket_obj)
                      st.session_state.ticket = ticket_obj.model_dump()
                      st.session_state.chat_log = [m.model_dump() for m in ticket_obj.chat_log]
                      st.session_state.pipeline_stage = 'in_progress'
                  st.rerun()
  
          elif st.session_state.pipeline_stage == 'in_progress':
              st.divider()
              st.subheader('📄 Solution Proposal')
              col1, col2 = st.columns(2)
              with col1: st.metric('Estimated Cost', t.get('estimated_cost','TBD'))
              with col2: st.metric('Timeline',        t.get('timeline','TBD'))
              st.info(t.get('solution_details','No details yet.'))
              st.caption(t.get('notes',''))
  
  # ══════════════════════════════════════════════════════
  # TAB 4 — TEAM LEAD MONITOR
  # ══════════════════════════════════════════════════════
with tab4:
      st.subheader('👁️ Team Lead — Activity Monitor')
      st.info('Team Lead monitors all activity. Read-only view. No assignments are made here.')
  
      # Pipeline stage indicator
      stages = ['waiting_sales','pending_triage','triaged','in_progress']
      stage_labels = ['Waiting for Sales','Pending Triage','Triaged','In Progress']
      current = st.session_state.pipeline_stage
      idx = stages.index(current) if current in stages else 0
      st.progress((idx)/(len(stages)-1) if idx > 0 else 0)
      st.caption(f'Current stage: {stage_labels[idx]}')
      st.divider()
  
      if st.session_state.ticket:
          t = st.session_state.ticket
          st.subheader('📋 Ticket Overview')
          c1,c2,c3,c4 = st.columns(4)
          with c1: st.metric('Customer',    t.get('customer_name','—'))
          with c2: st.metric('Solution',    t.get('solution_type','—'))
          with c3: st.metric('Assigned To', t.get('assigned_to','Not yet'))
          with c4: st.metric('Status',      t.get('status','—').upper())
          if t.get('estimated_cost'):
              c1,c2 = st.columns(2)
              with c1: st.metric('Estimated Cost', t.get('estimated_cost','—'))
              with c2: st.metric('Timeline',       t.get('timeline','—'))
          st.divider()
          st.subheader('📜 Full Activity Log')
          for msg in st.session_state.chat_log:
              icon = {'sales':'🟢','triage':'🟡','specialist':'🔵','team_lead':'🟣'}.get(msg['role'],'⚪')
              st.markdown(f"{icon} **{msg['sender']}** `{msg['time']}`")
              st.markdown(f'> {msg["text"]}')
              st.divider()
      else:
          st.info('No active ticket. Waiting for Sales team to submit a request.')
  
      # Reset button — only Team Lead can reset
      st.divider()
      if st.button('🔄 Reset — Clear All and Start Fresh', type='secondary'):
          st.session_state.ticket = None
          st.session_state.chat_log = []
          st.session_state.pipeline_stage = 'waiting_sales'
          st.rerun()
