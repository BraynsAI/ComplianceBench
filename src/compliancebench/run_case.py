import argparse
import json
import os
import re

import xml.etree.ElementTree as ET
from pathlib import Path
from dotenv import load_dotenv
from omegaconf import OmegaConf

from compliancebench.llms import LLMClient, LLMClientModelConfig
from compliancebench.loaders.case import build_case_messages
from compliancebench.project import Project


def call_model(
        client: LLMClient, model_config: LLMClientModelConfig, messages: list[dict]
):
    response = client.call_model(messages)
    return response


def parse_xml_output(xml_output: str) -> dict:
    start = xml_output.find("<result>")
    end = xml_output.find("</result>") + len("</result>")
    xml_str = xml_output[start:end]
    root = ET.fromstring(xml_str)
    result = {
        "outcome": root.findtext("outcome"),
        "reasoning": [
            {"doc": p.get("doc"), "text": p.text} for p in root.find("reasoning")
        ],
        "actions": [a.text for a in root.find("actions")],
        "explanation": root.findtext("explanation"),
    }
    return result


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", required=True, help="path to a case folder")
    return ap.parse_args()

def score_output(parsed: dict, case_dir: Path) -> dict:
    """Layer-1 metrics computable from the answer alone.

    outcome_match:     1 if the outcome equals the expected disposition, else 0
                       (None when the case has no expected disposition).
    citation_validity: share of reasoning points citing a doc id that exists
                       in the case materials (None when nothing is cited).

    Findings coverage / hallucinated findings need per-case patterns and are
    scored elsewhere; the judge layer is separate.
    """
    case = OmegaConf.load(case_dir / "case.yaml")

    expected = case.get("expected_disposition")
    expected_norm = expected.strip().lower() if expected else None
    material_ids = {m.split("-", 1)[0] for m in case.get("materials", [])}

    model_outcome = parsed.get("outcome")
    model_norm = model_outcome.strip().lower() if model_outcome else None
    reasoning = parsed.get("reasoning", [])
    cites = [p["doc"] for p in reasoning]

    outcome_match = None
    if expected_norm is not None:
        outcome_match = int(model_norm == expected_norm)

    citation_validity = None
    if cites:
        citation_validity = round(sum(c in material_ids for c in cites) / len(cites), 2)

    return {
        "expected_outcome": expected,
        "model_outcome": model_outcome,
        "outcome_match": outcome_match,
        "citation_validity": citation_validity,
        "n_reasoning_points": len(reasoning),
        "n_actions": len(parsed.get("actions", [])),
    }


if __name__ == "__main__":
    load_dotenv()
    args = parse_args()
    case_dir = Path(args.case)
    if not case_dir.exists():
        raise FileNotFoundError(f"No such file or directory: {case_dir}")

    company_profile_dir = Project.data_dir / "profile"
    messages = build_case_messages(case_dir, company_profile_dir)
    config = LLMClientModelConfig(
        model_name="openai/br_llm", max_tokens=4096, temperature=0.0
    )
    client = LLMClient(model_config=config)
    answer = call_model(client, config, messages)

    parsed_answer = parse_xml_output(answer)
    print("Parsed output as JSON:\n", json.dumps(parsed_answer, indent=4))
    print(f"Scoring now")
    scores = score_output(parsed_answer, case_dir)
    print("Scores:\n", json.dumps(scores, indent=4))
