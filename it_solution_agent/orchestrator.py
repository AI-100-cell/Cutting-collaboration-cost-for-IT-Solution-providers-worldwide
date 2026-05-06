from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Optional
from shared.state import SolutionTicket
from agents.sales_agent import run_sales_agent
from agents.triage_agent import run_triage_agent
from agents.inside_solution_agent import run_inside_solution_agent

load_dotenv()

class GraphState(TypedDict):
    customer_name:    str
    customer_request: str
    ticket:           Optional[dict]
    error:            Optional[str]


def sales_node(state):
    print('\n[Team Lead] Sales node starting...')
    try:
        t = run_sales_agent(state['customer_name'], state['customer_request'])
        return {**state, 'ticket': t.model_dump(), 'error': None}
    except Exception as e:
        return {**state, 'error': str(e)}


def triage_node(state):
    print('\n[Team Lead] Triage node starting...')
    try:
        t = run_triage_agent(SolutionTicket(**state['ticket']))
        return {**state, 'ticket': t.model_dump(), 'error': None}
    except Exception as e:
        return {**state, 'error': str(e)}


def solution_node(state):
    print('\n[Team Lead] Solution node starting...')
    try:
        t = run_inside_solution_agent(SolutionTicket(**state['ticket']))
        return {**state, 'ticket': t.model_dump(), 'error': None}
    except Exception as e:
        return {**state, 'error': str(e)}


def check(state):
    if state.get('error'):
        print(f'[Team Lead] ERROR: {state["error"]} — stopping pipeline')
        return 'stop'
    return 'ok'


graph = StateGraph(GraphState)
graph.add_node('sales',    sales_node)
graph.add_node('triage',   triage_node)
graph.add_node('solution', solution_node)
graph.add_edge(START, 'sales')
graph.add_conditional_edges('sales',    check, {'ok':'triage',   'stop':END})
graph.add_conditional_edges('triage',   check, {'ok':'solution', 'stop':END})
graph.add_edge('solution', END)
pipeline = graph.compile()

def process_request(customer_name, customer_request):
    result = pipeline.invoke({
        'customer_name':    customer_name,
        'customer_request': customer_request,
        'ticket': None, 'error': None
    })
    return result.get('ticket', {})
