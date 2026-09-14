import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from dotenv import load_dotenv
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
