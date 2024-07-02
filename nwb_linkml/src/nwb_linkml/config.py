"""
Manage the operation of nwb_linkml from environmental variables
"""

import tempfile
from pathlib import Path

from pydantic import (
    DirectoryPath,
    Field,
    FieldValidationInfo,
    computed_field,
    field_validator,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """
    Configuration for nwb_linkml, populated by default but can be overridden
    by environment variables.

    Examples:

        export NWB_LINKML_CACHE_DIR="/home/mycache/dir"

    """

    model_config = SettingsConfigDict(env_prefix="nwb_linkml_")
    cache_dir: DirectoryPath = Field(
        default_factory=lambda: Path(tempfile.gettempdir()) / "nwb_linkml__cache",
        description="Location to cache generated schema and models",
    )

    @computed_field
    @property
    def linkml_dir(self) -> Path:
        """Directory to store generated linkml models"""
        return self.cache_dir / "linkml"

    @computed_field
    @property
    def pydantic_dir(self) -> Path:
        """Directory to store generated pydantic models"""
        return self.cache_dir / "pydantic"

    @computed_field
    @property
    def git_dir(self) -> Path:
        """Directory for :class:`nwb_linkml.providers.git.GitRepo` to clone to"""
        return self.cache_dir / "git"

    @field_validator("cache_dir", mode="before")
    @classmethod
    def folder_exists(cls, v: Path, info: FieldValidationInfo) -> Path:
        v = Path(v)
        v.mkdir(exist_ok=True)
        assert v.exists()
        return v

    @model_validator(mode="after")
    def folders_exist(self) -> "Config":
        for field, path in self.model_dump().items():
            if isinstance(path, Path):
                path.mkdir(exist_ok=True, parents=True)
                assert path.exists()
        return self

    def __post_init__(self):
        self.cache_dir.mkdir(exist_ok=True)
        self.linkml_dir.mkdir(exist_ok=True)
        self.pydantic_dir.mkdir(exist_ok=True)
        self.git_dir.mkdir(exist_ok=True)
