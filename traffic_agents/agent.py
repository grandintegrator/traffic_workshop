from google.adk.agents import (
    LlmAgent
)
from google.adk.tools import google_search
from .config import config
from .prompts import (
    INTERACTIVE_PLANNER_PROMPT,
    CCTV_ANALYSIS_PROMPT,
    RESEARCH_EXECUTOR_PROMPT,
    PLAN_GENERATOR_PROMPT,
    REPORT_COMPOSER_PROMPT
)
from .tools import (
    get_vehicle_count_by_type,
    get_toll_records_by_plate_number
)

from google.adk.tools.agent_tool import AgentTool
from google.adk.tools import load_artifacts

# from toolbox_core import ToolboxSyncClient

# toolbox = ToolboxSyncClient("http://127.0.0.1:5000")
# mcp_tools = toolbox.load_toolset('plate_reader_toolset')


cctv_analysis_agent = LlmAgent(
    model=config.planning_model,
    name="cctv_analysis_agent",
    description="Analyzes CCTV footage to identify safety violations, sequence of events, and contributing factors",
    instruction=CCTV_ANALYSIS_PROMPT,
    tools=[load_artifacts],
    output_key="research_findings",
)


plan_generator = LlmAgent(
    model=config.planning_model,
    name="plan_generator",
    description="Generates or refine the existing 5 line action-oriented safety investigation research plan using incident images and descriptions.",
    instruction=PLAN_GENERATOR_PROMPT,
)


internal_research_executor = LlmAgent(
    model=config.sub_agent_model,
    name="internal_research_executor",
    description="Executes comprehensive safety investigation research using database research.",
    instruction=RESEARCH_EXECUTOR_PROMPT,
    tools=[get_toll_records_by_plate_number, get_vehicle_count_by_type],
    output_key="research_findings"
)

report_composer = LlmAgent(
    model=config.base_model,
    name="report_composer_with_citations",
    include_contents="none",
    description="Transforms safety investigation research data and a markdown outline into a final, cited report.",
    instruction=REPORT_COMPOSER_PROMPT,
    output_key="final_report"
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
    instruction=INTERACTIVE_PLANNER_PROMPT,
    sub_agents=[research_coordinator_agent],
    tools=[AgentTool(plan_generator)],
    output_key="research_plan",
)

root_agent = interactive_planner_agent
