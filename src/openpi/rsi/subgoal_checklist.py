"""B1K-aligned Q-score style subgoal checklist metrics."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Subgoal:
    name: str
    done: bool = False


@dataclass
class Checklist:
    task_id: str
    subgoals: list[Subgoal] = field(default_factory=list)

    def mark(self, name: str, done: bool = True) -> None:
        for sg in self.subgoals:
            if sg.name == name:
                sg.done = done
                return
        raise KeyError(f"unknown subgoal: {name}")

    @property
    def completed(self) -> int:
        return sum(1 for sg in self.subgoals if sg.done)

    @property
    def total(self) -> int:
        return len(self.subgoals)


def q_score(checklist: Checklist) -> float:
    """Fraction of completed subgoals (BDDL/Q-score style partial credit)."""
    if checklist.total == 0:
        return 0.0
    return checklist.completed / checklist.total


def end_to_end_success(checklist: Checklist) -> bool:
    return checklist.total > 0 and checklist.completed == checklist.total


def summarize_episode(checklist: Checklist) -> dict:
    return {
        "task_id": checklist.task_id,
        "n_subgoals": checklist.total,
        "n_completed": checklist.completed,
        "q_score": q_score(checklist),
        "e2e_success": end_to_end_success(checklist),
        "subgoals": [{"name": s.name, "done": s.done} for s in checklist.subgoals],
    }
