from dataclasses import dataclass
from pathlib import Path


@dataclass
class Project:
    """
    This class represents our project.
    It stores useful information about the structure
    """

    module_dir: Path = Path(__file__).parent
    project_dir: Path = Path(__file__).parents[2]

    configs_dir = project_dir / "configs"

    data_dir = project_dir / "data"
    log_dir = project_dir / "log"

    outputs_dir = project_dir / "outputs"

    def __post_init__(self) -> None:
        # create the directories if they don't exist
        pass


if __name__ == "__main__":
    project = Project()
    print(f"Project outputs directory: {project.outputs_dir}")
    print(f"Project data directory: {project.data_dir}")
