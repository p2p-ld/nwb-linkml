"""
Patching the source code at different stages of the code generation process
"""

import argparse
import pprint
import re
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import ClassVar, List


class Phases(StrEnum):
    """Phases of the loading and generation process"""

    post_generation_pydantic = "post_generation_pydantic"
    post_load_yaml = "post_load_yaml"
    """After the yaml of the nwb schema classes is loaded"""


@dataclass
class Patch:
    """
    Structured change to make to generated models
    """

    phase: Phases
    path: Path
    """Path relative to repository root"""
    match: str
    """Regex to match the thing to be replaced"""
    replacement: str
    """Regex to replace with (eg. can use capturing groups in match)"""

    instances: ClassVar[List["Patch"]] = []
    """
    List of patches!
    """

    def __post_init__(self):
        self.instances.append(self)


### Patches

## Patches for the generated pydantic classes

patch_schema_slot = Patch(
    phase=Phases.post_generation_pydantic,
    path=Path("src/nwb_schema_language/datamodel/nwb_schema_pydantic.py"),
    match=r"\n\s*(schema:)(.*Field\()(.*)",
    replacement=r'\n    schema_:\2alias="schema", \3',
)

patch_dtype_single_multiple = Patch(
    phase=Phases.post_generation_pydantic,
    path=Path("src/nwb_schema_language/datamodel/nwb_schema_pydantic.py"),
    match=r"(\n\s*dtype: Optional\[)List\[Union\[CompoundDtype, (FlatDtype, ReferenceDtype\]\])\]",
    replacement=r"\1Union[List[CompoundDtype], \2",
)

patch_author_single_multiple = Patch(
    phase=Phases.post_generation_pydantic,
    path=Path("src/nwb_schema_language/datamodel/nwb_schema_pydantic.py"),
    match=r"author: List\[str\]",
    replacement="author: List[str] | str",
)

patch_contact_single_multiple = Patch(
    phase=Phases.post_generation_pydantic,
    path=Path("src/nwb_schema_language/datamodel/nwb_schema_pydantic.py"),
    match=r"contact: List\[str\]",
    replacement="contact: List[str] | str",
)


def run_patches(phase: Phases, verbose: bool = False) -> None:
    """
    Apply all declared :class:`.Path` instances
    """
    patches = [p for p in Patch.instances if p.phase == phase]
    for patch in patches:
        if verbose:
            print("Patching:")
            pprint.pprint(patch)
        with open(patch.path) as pfile:
            string = pfile.read()
        string = re.sub(patch.match, patch.replacement, string)
        with open(patch.path, "w") as pfile:
            pfile.write(string)


def main() -> None:
    """
    Run patches from the command line
    """
    parser = argparse.ArgumentParser(description="Run patches for a given phase of code generation")
    parser.add_argument("--phase", choices=list(Phases.__members__.keys()), type=Phases)
    args = parser.parse_args()
    run_patches(args.phase, verbose=True)
