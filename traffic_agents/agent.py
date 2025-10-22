from google.adk.agents import (
    LlmAgent
)
from google.adk.tools import google_search
from .config import config
from .prompts import (
    interactive_planner_prompt,
    plan_generator_prompt,
    research_evaluator_prompt,
)
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools import load_artifacts
from .models import InvestigationFeedback
from google.adk.planners import BuiltInPlanner
from google.genai import types as genai_types
from typing import AsyncGenerator
from google.adk.events import Event, EventActions
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents import Agent

from toolbox_core import ToolboxSyncClient

toolbox = ToolboxSyncClient("http://127.0.0.1:5000")
mcp_tools = toolbox.load_toolset('tolls-toolset')


cctv_analysis_agent = LlmAgent(
    model=config.planning_model,
    name="cctv_analysis_agent",
    description="Analyzes CCTV footage to identify safety violations, sequence of events, and contributing factors",
    instruction="""
    ...REWORD
    """,
    tools=[load_artifacts],
    output_key="research_findings",
)


plan_generator = LlmAgent(
    model=config.planning_model,
    name="plan_generator",
    description="Generates or refine the existing 5 line action-oriented safety investigation research plan using incident images and descriptions.",
    instruction=plan_generator_prompt
)


internal_research_executor = LlmAgent(
    model=config.sub_agent_model,
    name="internal_research_executor",
    description="Executes comprehensive safety investigation research using database research.",
    instruction="""
    You are a specialist safety investigation researcher. You have access to the following tools:
    
    - get_badge_id_by_name: Ask the user for the name of the person on site at the time of the incident.
    - get_swipe_card_data_by_id: Use the card id to get the swipe card data of the person on site at the time of the incident. 
    
    This will return all of the historical swipe card data for this person. Check if the person was on site at the time of the incident.
    You are part of a larger team of agents, do not greet users, ask clarifying questions and output your findings.

    - Add your findings to the 'research_findings' state key.

    IMPORTANT: Once you have completed your research, return to the parent *research_coordinator_agent* agent.
    """,
    tools=[mcp_tools],
    output_key="research_findings"
)

research_coordinator_agent = LlmAgent(
    name="research_coordinator_agent",
    description="Executes a pre-approved safety investigation research plan. It performs iterative research, evaluation, and composes a final, cited report.",
    instruction="""
    You are a safety investigation researcher. You will follow a STRICT two step process to complete your task:
    1. You are to start with the *cctv_analysis_agent*
    2. Use the *data_research_executor* agent to research an incident.
    IMPORTANT: IMMEDIATELY after these two agents, you are to use the *report_composer* agent to compose a final safety incident report.
    """,
    sub_agents=[
        cctv_analysis_agent,
        internal_research_executor,
        report_composer,
    ],
)


interactive_planner_agent = LlmAgent(
    name="interactive_planner_agent",
    model=config.sub_agent_model,
    description="The primary safety investigation research assistant. It collaborates with the user to create a safety investigation research plan, and then executes it upon approval.",
    instruction=interactive_planner_prompt,
    sub_agents=[research_coordinator_agent],
    tools=[AgentTool(plan_generator)],
    output_key="research_plan",
)

report_composer = LlmAgent(
    model=config.base_model,
    name="report_composer_with_citations",
    include_contents="none",
    description="Transforms safety investigation research data and a markdown outline into a final, cited report.",
    instruction=f"""
    Transform the provided safety investigation data into a polished, professional, and meticulously crafted safety investigation report.

    ---
    ### INPUT DATA
    *   Safety Investigation Research Plan: {{research_plan}}
    *   Safety Investigation Research Findings: {{research_findings}}
    ---
    ### Final Instructions
    Generate a comprehensive safety investigation report.
    The final report must strictly follow the structure provided in the **Report Structure** markdown outline.
    Do not include a "References" or "Sources" section; all citations must be in-line.

    Research report should be verbose and detailed and mention the following sections and keywords.

    Incident Description: This section outlines what happened, why it happened, immediate actions taken, and the actual and potential consequences.
    Casual Factor and Root Cause: It identifies the causal factors, root causes, and opportunities for improvement, along with a timeline of the incident 
    Basic Causes: This section details the basic causes, including causal factors and root causes, along with findings 
    Corrective Action: It lists actions to address causal factors and root causes, accountability, status, and due dates 
    Opportunities for Improvement: This section describes opportunities for improvement, accountability, status, and due dates 
    HPE/H Classification Decision Workflow: It explains the classification recommendation for the incident 
    Supporting Information: Additional supporting information related to the incident 
    Control Barrier Analysis: Analysis of prescribed controls that were absent or ineffective 
    Assurance Activities: Details assurance activities, findings, and previous incident reviews
    PEEPO: A structure for key incident data collection 
    ICAM Chart: Analysis of organisational factors, task/environmental conditions, individual/team actions, absent or failed defences, and positives
    TapRooT SnapChart: Example for TapRooT incident analysis
    HFAT Summary: Summary of HFAT incident analysis 
    HPE Classifications - Decision Workflow: Decision workflow for HPE classifications
    
    **Action Items**

    Corrective Actions: Actions to address causal factors and root causes, including hierarchy of control, accountability, status, and due dates.
    Opportunities for Improvement: Description of opportunities for improvement, accountability, status, and due dates.
    Assurance Activities: Assurance activities, findings, and previous incident reviews. 
    """,
    output_key="final_cited_report"
)