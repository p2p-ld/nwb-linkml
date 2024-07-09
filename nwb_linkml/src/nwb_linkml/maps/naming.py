"""
String manipulation methods for names
"""

import re
from pathlib import Path

CAMEL_TO_SNAKE = re.compile(r"((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))")
"""
Convert camel case to snake case

courtesy of: https://stackoverflow.com/a/12867228
"""


def snake_case(name: str | None) -> str | None:
    """
    Snake caser for replacing all non-word characters with single underscores

    Primarily used when creating dimension labels in
    :class:`~nwb_linkml.adapters.ArrayAdapter` , see also :func:`.camel_to_snake`
    for converting camelcased names.
    """
    if name is None:
        return None

    name = name.strip()
    name = re.sub(r"\W+", "_", name)
    name = name.lower()
    return name


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


def relative_path(target: Path, origin: Path) -> Path:
    """
    return path of target relative to origin, even if they're
    not in the same subpath

    References:
        - https://stackoverflow.com/a/71874881
    """

    def _relative_path(target: Path, origin: Path) -> Path:
        try:
            return Path(target).resolve().relative_to(Path(origin).resolve())
        except ValueError:  # target does not start with origin
            # recursion with origin (eventually origin is root so try will succeed)
            return Path("..").joinpath(_relative_path(target, Path(origin).parent))

    try:
        successful = Path(target).resolve().relative_to(Path(origin).resolve())
        return successful
    except ValueError:  # target does not start with origin
        # recursion with origin (eventually origin is root so try will succeed)
        relative = Path("..").joinpath(_relative_path(target, Path(origin).parent))
        # remove the first '..' because this thing freaking double counts
        return Path(*relative.parts[1:])
