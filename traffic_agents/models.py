from pydantic import BaseModel, Field
from typing import Literal


class InvestigationQuery(BaseModel):
    """Model representing a specific search query for safety investigation research."""
    
    search_query: str = Field(
        description="A highly specific and targeted query for safety investigation research and web search."
    )


class InvestigationFeedback(BaseModel):
    """Model for providing evaluation feedback on safety investigation research quality."""

    grade: Literal["pass", "fail"] = Field(
        description="Evaluation result. 'pass' if the safety investigation research is sufficient, 'fail' if it needs revision."
    )
    comment: str = Field(
        description="Detailed explanation of the evaluation, highlighting strengths and/or weaknesses investigation research."
    )
    follow_up_queries: list[InvestigationQuery] | None = Field(
        default=None,
        description="A list of specific, targeted follow-up search queries needed to fix safety investigation research gaps. This should be null or empty if the grade is 'pass'.",
    )
