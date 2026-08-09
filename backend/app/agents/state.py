import operator
from typing import TypedDict, Annotated


class AgentState(TypedDict, total=False):
    analysis_id: int
    repo_id: int
    kind: str
    question: str
    route: str
    evidence: list[dict]
    worker_tasks: list[str]
    worker_task: str
    findings: Annotated[list[dict], operator.add]
    synthesis: dict
    evaluation: dict
    final_report: dict
    attempt: int
