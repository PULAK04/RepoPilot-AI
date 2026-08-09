import json
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from app.agents.state import AgentState
from app.services.llm import llm
from app.services.vector_store import vector_store
from app.services.progress import progress_service


def _compact_evidence(evidence: list[dict], max_chars: int = 24000) -> str:
    pieces = []
    used = 0
    for item in evidence:
        block = f"\nFILE: {item['path']} lines {item.get('start_line')}-{item.get('end_line')} score={item.get('score', 0):.3f}\n{item.get('text','')}\n"
        if used + len(block) > max_chars:
            break
        pieces.append(block)
        used += len(block)
    return "".join(pieces)


def router_node(state: AgentState):
    progress_service.set(state["analysis_id"], 10, "Router agent is classifying the task")
    kind = state.get("kind", "ask")
    fallback_route = {
        "bug": "bug_investigation",
        "code_review": "code_review",
        "architecture": "architecture",
        "tests": "test_generation",
        "performance": "performance",
        "ask": "codebase_question",
    }.get(kind, "codebase_question")
    data = llm.complete_json(
        "You are the routing agent for a software repository analysis system.",
        f"Classify this request. Allowed routes: bug_investigation, code_review, architecture, test_generation, performance, codebase_question.\nRequest kind: {kind}\nQuestion: {state['question']}\nReturn {{\"route\":\"...\",\"reason\":\"...\"}}",
        {"route": fallback_route, "reason": "Mapped from requested analysis kind."},
    )
    route = data.get("route", fallback_route)
    if route not in {"bug_investigation", "code_review", "architecture", "test_generation", "performance", "codebase_question"}:
        route = fallback_route
    return {"route": route, "findings": [], "attempt": state.get("attempt", 0)}


def research_node(state: AgentState):
    attempt = state.get("attempt", 0)
    progress_service.set(state["analysis_id"], 25 if attempt == 0 else 60, "RAG research is retrieving relevant repository evidence")
    query = state["question"]
    if attempt:
        query += " implementation call sites configuration tests edge cases related code"
    evidence = vector_store.search(state["repo_id"], query, limit=14 if attempt == 0 else 18)
    return {"evidence": evidence}


def orchestrator_node(state: AgentState):
    progress_service.set(state["analysis_id"], 38, "Orchestrator is decomposing the investigation")
    route = state["route"]
    defaults = {
        "bug_investigation": [
            "Trace the likely code path and identify logic defects related to the reported behavior.",
            "Inspect API boundaries, validation, authentication, async/error handling, and external service interactions.",
            "Inspect persistence/database/cache behavior and identify state consistency problems.",
            "Look for missing tests, edge cases, regressions, and assumptions that should be verified.",
        ],
        "code_review": [
            "Review correctness and error handling.",
            "Review maintainability, coupling, duplication, naming and architecture.",
            "Review security and input/data handling risks visible in the supplied code.",
            "Review performance, database/API usage and avoidable repeated work.",
        ],
        "architecture": [
            "Infer major modules, responsibilities and boundaries.",
            "Infer request/data flow and important integrations.",
            "Identify persistence, caching, queues and external services.",
            "Identify architecture risks, scaling constraints and improvement opportunities.",
        ],
        "test_generation": [
            "Identify the highest-value functions/endpoints to test from the retrieved evidence.",
            "Design success, failure, boundary and authorization test cases.",
            "Infer the likely repository test framework and produce implementation-ready test suggestions without inventing APIs.",
        ],
        "performance": [
            "Inspect data-access patterns, repeated work, loops and likely N+1 or excessive-query behavior.",
            "Inspect external/API calls, sequential independent operations, payload size and pagination/caching opportunities.",
            "Inspect architecture-level latency, queueing, caching and scalability risks visible in the repository evidence.",
        ],
        "codebase_question": [
            "Answer the question directly from the most relevant code evidence and trace the involved files/functions.",
            "Cross-check the answer against adjacent configuration, call sites and data models.",
        ],
    }
    fallback = defaults[route]
    evidence_summary = "\n".join(f"- {e['path']}" for e in state.get("evidence", [])[:12])
    data = llm.complete_json(
        "You are an engineering orchestrator. Break a repository question into complementary specialist investigations. Keep tasks non-overlapping and evidence-driven.",
        f"Route: {route}\nQuestion: {state['question']}\nRetrieved files:\n{evidence_summary}\nReturn JSON {{\"tasks\":[\"...\"]}} with 2-4 tasks.",
        {"tasks": fallback},
    )
    tasks = data.get("tasks") or fallback
    tasks = [str(t) for t in tasks][:4]
    return {"worker_tasks": tasks}


def dispatch_workers(state: AgentState):
    common = {
        "analysis_id": state["analysis_id"],
        "repo_id": state["repo_id"],
        "kind": state["kind"],
        "question": state["question"],
        "route": state["route"],
        "evidence": state.get("evidence", []),
        "attempt": state.get("attempt", 0),
    }
    return [Send("worker", {**common, "worker_task": task}) for task in state.get("worker_tasks", [])]


def worker_node(state: AgentState):
    task = state.get("worker_task", "Analyze the relevant code.")
    evidence = _compact_evidence(state.get("evidence", []), 18000)
    fallback = {
        "task": task,
        "summary": "LLM is not configured; relevant repository evidence was retrieved for this specialist task.",
        "severity": "info",
        "confidence": 0.35,
        "evidence": [
            {"path": e["path"], "lines": f"{e.get('start_line')}-{e.get('end_line')}"}
            for e in state.get("evidence", [])[:4]
        ],
    }
    data = llm.complete_json(
        "You are a senior software engineer working as one specialist in a multi-agent repository investigation. Make claims only when supported by the supplied repository snippets. Do not invent files, functions or runtime behavior. If evidence is insufficient, say so.",
        f"Main request: {state['question']}\nSpecialist task: {task}\nRepository evidence:\n{evidence}\nReturn JSON with keys task, summary, severity (info/low/medium/high/critical), confidence (0-1), evidence (array of path/lines/reason), and recommendations (array).",
        fallback,
    )
    data["task"] = data.get("task", task)
    return {"findings": [data]}


def reducer_node(state: AgentState):
    progress_service.set(state["analysis_id"], 72, "Reducer is synthesizing specialist findings and a proposed fix")
    findings = state.get("findings", [])
    evidence = _compact_evidence(state.get("evidence", []), 14000)
    fallback = {
        "summary": "Specialist findings were collected. Configure an LLM API key for a higher-quality root-cause synthesis.",
        "root_cause": findings[0].get("summary") if findings else "Insufficient evidence.",
        "suggested_fix": "Review the retrieved files and verify the suspected path before making changes.",
        "risk": "unknown",
        "files_to_review": list(dict.fromkeys(e["path"] for e in state.get("evidence", [])[:6])),
    }
    data = llm.complete_json(
        "You are the reducer/fix agent. Synthesize multiple specialist findings into one precise engineering conclusion. Prefer the simplest explanation supported by evidence. Do not fabricate code or line numbers. If the user asked a general codebase question, answer it directly instead of forcing a bug root cause.",
        f"Request: {state['question']}\nRoute: {state['route']}\nFindings:\n{json.dumps(findings, ensure_ascii=False)[:18000]}\nEvidence excerpts:\n{evidence}\nReturn JSON with summary, root_cause, suggested_fix, risk, files_to_review, and optional_patch (string or null).",
        fallback,
    )
    return {"synthesis": data}


def evaluator_node(state: AgentState):
    progress_service.set(state["analysis_id"], 86, "Evaluator is checking evidence grounding and completeness")
    attempt = state.get("attempt", 0)
    evidence_paths = [e["path"] for e in state.get("evidence", [])]
    fallback_pass = bool(state.get("evidence"))
    fallback = {
        "passed": fallback_pass,
        "confidence": 0.55 if fallback_pass else 0.1,
        "reason": "Fallback evaluator checks whether repository evidence was retrieved.",
        "missing": [] if fallback_pass else ["No repository evidence was retrieved."],
    }
    data = llm.complete_json(
        "You are a strict evaluator for an AI software-engineering assistant. Check whether the synthesis is actually grounded in the retrieved repository evidence and whether it answers the user's request. Do not reward confident unsupported claims.",
        f"Request: {state['question']}\nSynthesis: {json.dumps(state.get('synthesis', {}), ensure_ascii=False)}\nAvailable evidence paths: {evidence_paths}\nReturn JSON {{\"passed\":true/false,\"confidence\":0-1,\"reason\":\"...\",\"missing\":[...]}}.",
        fallback,
    )
    return {"evaluation": data, "attempt": attempt + 1}


def evaluation_route(state: AgentState):
    passed = bool(state.get("evaluation", {}).get("passed"))
    if not passed and state.get("attempt", 1) < 2:
        return "retry"
    return "finalize"


def finalize_node(state: AgentState):
    progress_service.set(state["analysis_id"], 96, "Final engineering report is being assembled")
    report = {
        "route": state.get("route"),
        "question": state.get("question"),
        "summary": state.get("synthesis", {}).get("summary"),
        "root_cause": state.get("synthesis", {}).get("root_cause"),
        "suggested_fix": state.get("synthesis", {}).get("suggested_fix"),
        "optional_patch": state.get("synthesis", {}).get("optional_patch"),
        "risk": state.get("synthesis", {}).get("risk"),
        "files_to_review": state.get("synthesis", {}).get("files_to_review", []),
        "evaluation": state.get("evaluation", {}),
        "findings": state.get("findings", []),
        "evidence": [
            {
                "path": e.get("path"),
                "start_line": e.get("start_line"),
                "end_line": e.get("end_line"),
                "score": round(float(e.get("score", 0)), 4),
                "snippet": e.get("text", "")[:1400],
            }
            for e in state.get("evidence", [])[:10]
        ],
        "attempts": state.get("attempt", 1),
    }
    return {"final_report": report}


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("router", router_node)
    graph.add_node("research", research_node)
    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("worker", worker_node)
    graph.add_node("reducer", reducer_node)
    graph.add_node("evaluator", evaluator_node)
    graph.add_node("finalize", finalize_node)

    graph.add_edge(START, "router")
    graph.add_edge("router", "research")
    graph.add_edge("research", "orchestrator")
    graph.add_conditional_edges("orchestrator", dispatch_workers, ["worker"])
    graph.add_edge("worker", "reducer")
    graph.add_edge("reducer", "evaluator")
    graph.add_conditional_edges("evaluator", evaluation_route, {"retry": "research", "finalize": "finalize"})
    graph.add_edge("finalize", END)
    return graph.compile()


repo_graph = build_graph()
