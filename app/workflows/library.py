from app.workflows.protocol import Workflow


class WorkflowNotFoundError(LookupError):
    """Raised when a requested workflow is not registered."""


class DuplicateWorkflowError(ValueError):
    """Raised when a workflow name is already registered."""


class WorkflowLibrary:
    def __init__(self) -> None:
        self._workflows: dict[str, Workflow] = {}

    def register(self, workflow: Workflow) -> None:
        name = workflow.name.strip()

        if not name:
            raise ValueError("Le nom du workflow ne peut pas être vide.")

        if name in self._workflows:
            raise DuplicateWorkflowError(
                f"Le workflow {name!r} est déjà enregistré."
            )

        self._workflows[name] = workflow

    def get(self, name: str) -> Workflow:
        try:
            return self._workflows[name]
        except KeyError as exc:
            raise WorkflowNotFoundError(
                f"Le workflow {name!r} est introuvable."
            ) from exc

    def names(self) -> tuple[str, ...]:
        return tuple(self._workflows)

    def all(self) -> tuple[Workflow, ...]:
        return tuple(self._workflows.values())

    def __len__(self) -> int:
        return len(self._workflows)

    def register_defaults(self) -> None:
        from app.workflows.demo_workflow import DemoWorkflow
        from app.workflows.pet_xp_workflow import PetXpWorkflow

        self.register(DemoWorkflow())
        self.register(PetXpWorkflow())