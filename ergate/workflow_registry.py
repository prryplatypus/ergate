from typing import Iterator

from .workflow import Workflow


class WorkflowRegistry:
    def __init__(self) -> None:
        self._workflows: dict[str, Workflow] = {}

    def __getitem__(self, unique_name: str) -> Workflow:
        try:
            return self._workflows[unique_name]
        except KeyError:
            raise KeyError(f'No workflow named "{unique_name}" is registered') from None

    def __iter__(self) -> Iterator[Workflow]:
        return iter(self._workflows.values())

    def register(self, workflow: Workflow) -> None:
        if workflow.unique_name in self._workflows:
            err = f'A workflow named "{workflow.unique_name}" is already registered'
            raise ValueError(err)
        self._workflows[workflow.unique_name] = workflow.register()
