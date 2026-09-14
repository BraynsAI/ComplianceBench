# Python stdlib
import os
from pathlib import Path

# Project Dependencies
from omegaconf import DictConfig, OmegaConf

# Project Imports
from compliancebench.constants import SYSTEM_PROMPT


def build_case_messages(case_dir: Path, profile_dir: Path):
    messages = [SYSTEM_PROMPT]
    user_message_packs = []
    # The pack slice. In production you attach the full text of the SOPs the
    # case lists (pdftotext on the files in pack/). The skeleton lists them.
    case_yaml_file = case_dir / "case.yaml"
    if not case_yaml_file.exists():
        raise FileNotFoundError(f"No such file or directory: {case_yaml_file}")
    case_yaml: DictConfig = OmegaConf.load(case_yaml_file)
    referenced_sops = case_yaml.get("sop_refs", [])
    # Sometimes referenced SOPS contain alos the section number, e.g. "SOP-01 1.2.3".
    # We only want the SOP ID.
    referenced_sops = [x.split(" ")[0].lower() for x in referenced_sops]

    user_message_packs.append("<sop>\n")
    for ref in referenced_sops:
        stem = ref.lower()
        hits = list(profile_dir.glob(f"**/{stem}*.txt"))
        if hits:
            # SOP have unique names, so there shouldn't be more than one hit.
            sop = hits[0]
            raw_sop = Path(sop).read_text(encoding="utf-8", errors="ignore")

            user_message_packs.append(
                f'<document id="{ref}" name="{os.path.basename(sop)}">\n'
                f"{raw_sop}\n</document>\n"
            )
        else:
            raise FileNotFoundError(f"No SOP file found for reference: {ref}")
    user_message_packs.append("</sop>\n")
    user_message_packs.append("<case_documents>\n")
    case_materials_path = case_dir / "materials"
    if not case_materials_path.exists():
        raise FileNotFoundError(f"No such directory: {case_materials_path}")
    material_docs = list(case_materials_path.glob("m*.txt"))
    for txt in sorted(material_docs):
        doc_id = txt.stem.split("-")[0]  # m01, m02 ...
        name = txt.stem.split("-")[1]  # human name
        raw = Path(txt).read_text(encoding="utf-8", errors="ignore")
        user_message_packs.append(
            f'<document id="{doc_id}" name="{name}">\n{raw}\n</document>\n'
        )
    user_message_packs.append("</case_documents>\n")
    user_message_content = "\n".join(user_message_packs)
    user_message = {"role": "user", "content": user_message_content}
    messages.append(user_message)
    return messages


if __name__ == "__main__":
    pass
