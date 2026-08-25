"""HiStrA-Python: structural analysis solver port."""
from histra.io.hr_loader import load_model
from histra.solver.backend_api import (
    ConcreteInterfaceMutation,
    PythonAnalysisRequest,
    PythonAnalysisResult,
    PythonSolverJobError,
    PythonSolverJobResult,
    PythonSolverTimeout,
    run_python_solver_job,
)
from histra.solver.cancellation import (
    CANCELLED_EXIT_CODE,
    CancelCheck,
    SolverCancelled,
)
from histra.solver.equilibrium import (
    UNSAFE_EQUILIBRIUM_EXIT_CODE,
    EquilibriumAudit,
    UnsafeEquilibriumWarning,
)
from histra.solver.capabilities import (
    SolverCapabilityIssue,
    SolverCapabilityReport,
    UnsupportedSolverCapability,
    inspect_solver_capabilities,
)
from histra.solver.outcomes import AnalysisExecution, AnalysisOutcome, AnalysisStep
from histra.solver.output_projection import (
    OutputProjectionError,
    UnsupportedOutputError,
    ModelPointDisplacement,
    compute_model_point_displacements,
    project_analysis_outputs,
    project_displacements,
    project_reactions,
)
from histra.solver.session import AnalysisSession, AnalysisSessionError
from histra.solver.modal import (
    ModalAnalysisError,
    ModalAnalysisResult,
    ModalMode,
    solve_modal_analysis,
)

__version__ = "0.3.0"

__all__ = [
    "__version__",
    "load_model",
    "AnalysisSession",
    "AnalysisSessionError",
    "solve_modal_analysis",
    "ModalAnalysisError",
    "ModalAnalysisResult",
    "ModalMode",
    "AnalysisExecution",
    "AnalysisOutcome",
    "AnalysisStep",
    "CANCELLED_EXIT_CODE",
    "CancelCheck",
    "SolverCancelled",
    "UNSAFE_EQUILIBRIUM_EXIT_CODE",
    "EquilibriumAudit",
    "UnsafeEquilibriumWarning",
    "SolverCapabilityIssue",
    "SolverCapabilityReport",
    "UnsupportedSolverCapability",
    "inspect_solver_capabilities",
    "OutputProjectionError",
    "UnsupportedOutputError",
    "ModelPointDisplacement",
    "compute_model_point_displacements",
    "project_analysis_outputs",
    "project_displacements",
    "project_reactions",
    "ConcreteInterfaceMutation",
    "PythonAnalysisRequest",
    "PythonAnalysisResult",
    "PythonSolverJobError",
    "PythonSolverJobResult",
    "PythonSolverTimeout",
    "run_python_solver_job",
]
