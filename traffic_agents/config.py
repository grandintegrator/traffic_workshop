from dataclasses import dataclass

@dataclass
class AgentConfiguration:
    base_model: str = "gemini-2.5-pro"
    sub_agent_model: str = "gemini-2.5-flash"
    planning_model: str = "gemini-2.5-pro"
    max_search_iterations: int = 5
    PROJECT_ID: str = "ajmalaziz-814-20250326021733"
    COMPANY_NAME: str = "Transurban"

config = AgentConfiguration()
