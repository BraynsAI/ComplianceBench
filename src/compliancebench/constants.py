# Python stdlib
from pathlib import Path
# Project Dependencies
from omegaconf import DictConfig, OmegaConf, ListConfig
# Project Imports
from compliancebench.project import Project


def _load_expected_outcomes(module: str) -> list[str]:
    file_path = Project.data_dir / 'expected_outcomes.yaml'
    if not file_path.exists():
        raise FileNotFoundError(f"No such file or directory: {file_path}")
    module_type = "-".join(module.split("-")[:2])
    expected_outcomes: DictConfig = OmegaConf.load(file_path)
    if module_type not in expected_outcomes:
        raise ValueError(f"Module type '{module_type}' not found in expected outcomes.")
    expected = expected_outcomes[module_type]
    if isinstance(expected, ListConfig):
        expected = [x.strip() for x in expected]
    if not isinstance(expected, list):
        raise ValueError(
            f"Expected outcomes for module type '{module_type}' should be a list.")
    return expected


def build_system_prompt(case_name: str) -> dict:
    expected_outcomes = _load_expected_outcomes(case_name)
    prompt = {
        "role": "system",
        "content": (
            "<instruction>\n"
            "You are an analyst at Mynta AB. Process the case in the documents below. "
            "Follow the SOPs. "
            f"The outcome must be exactly one of these words: {expected_outcomes}."
            "Answer only in the result format:\n"
            "<result>"
            "<outcome>...</outcome>"
            '<reasoning><point doc="mXX">...</point></reasoning>'
            "<actions><action>...</action></actions>"
            "<explanation>...</explanation>"
            "</result>\n"
            "</instruction>\n"
        )
    }
    return prompt


if __name__ == "__main__":
    case_dir = Path("data/cases/M1-KYB-001")
    import os


    print(case_dir.exists())
    print(os.path.basename(os.path.normpath(case_dir)))
    prompt = build_system_prompt(case_dir.stem)
    print(prompt)
