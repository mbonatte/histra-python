"""Model preparation and readiness validation."""

from .cache import (
    get_model_cache_path,
    is_cache_enabled,
    load_prepared_cache,
    save_prepared_cache,
)
from .errors import ModelPreparationError
from .lateral_subgrade import set_lateral_subgrade_moduli
from .prepare_model import (
    PreparationReport,
    create_brand_new_model,
    prepare_model,
    rebuild_interface_springs,
)
from .validation import (
    ModelPreprocessingRequiredError,
    ModelReadinessReport,
    inspect_solver_readiness,
    require_solver_ready,
)

__all__ = [
    "ModelPreparationError",
    "set_lateral_subgrade_moduli",
    "PreparationReport",
    "create_brand_new_model",
    "prepare_model",
    "rebuild_interface_springs",
    "ModelPreprocessingRequiredError",
    "ModelReadinessReport",
    "inspect_solver_readiness",
    "require_solver_ready",
    "get_model_cache_path",
    "is_cache_enabled",
    "load_prepared_cache",
    "save_prepared_cache",
]
