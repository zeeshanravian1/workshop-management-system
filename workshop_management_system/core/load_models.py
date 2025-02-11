"""Load all models module.

Description:
- This module is used to load all SQLModel models from project.

"""

from importlib import import_module
from pathlib import Path


def load_all_models() -> None:
    """Load SQLModel models from project.

    Description:
    - This function is used to load all SQLModel models from project.

    :Args:
    - `None`

    :Returns:
    - `None`

    """
    base_path: Path = Path(__file__).resolve().parent.parent.parent

    # Discover all Python files in project
    for path in base_path.rglob(pattern="model.py"):
        if "site-packages" in str(object=path):
            continue

        try:
            # Import module
            import_module(
                name=".".join(
                    path.relative_to(base_path).with_suffix(suffix="").parts
                )
            )
        except ModuleNotFoundError:
            continue
