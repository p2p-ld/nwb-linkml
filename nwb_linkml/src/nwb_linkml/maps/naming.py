import pdb
import re
from pathlib import Path

CAMEL_TO_SNAKE = re.compile("((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))")
"""
Convert camel case to snake case

courtesy of: https://stackoverflow.com/a/12867228
"""


def camel_to_snake(name: str) -> str:
    """
    Convert camel case to snake case

    courtesy of: https://stackoverflow.com/a/12867228
    """
    return CAMEL_TO_SNAKE.sub(r"_\1", name).lower()


def module_case(name: str) -> str:
    """
    Returns name that can be used as a python module, used for
    referring to generated pydantic and linkml models.

    Replaces with underscores:
        - -
        - .
    """
    return name.replace("-", "_").replace(".", "_").replace("/", ".").lower()


def version_module_case(name: str) -> str:
    """
    :func:`.module_case` except ensure that it starts with "v"
    """
    name = module_case(name)
    if not name.startswith("v"):
        name = "v" + name
    return name


def relative_path(target: Path, origin: Path):
    """
    return path of target relative to origin, even if they're
    not in the same subpath

    References:
        - https://stackoverflow.com/a/71874881
    """

    def _relative_path(target: Path, origin: Path):
        try:
            return Path(target).resolve().relative_to(Path(origin).resolve())
        except ValueError as e:  # target does not start with origin
            # recursion with origin (eventually origin is root so try will succeed)
            return Path("..").joinpath(_relative_path(target, Path(origin).parent))

    try:
        successful = Path(target).resolve().relative_to(Path(origin).resolve())
        return successful
    except ValueError as e:  # target does not start with origin
        # recursion with origin (eventually origin is root so try will succeed)
        relative = Path("..").joinpath(_relative_path(target, Path(origin).parent))
        # remove the first '..' because this thing freaking double counts
        return Path(*relative.parts[1:])
