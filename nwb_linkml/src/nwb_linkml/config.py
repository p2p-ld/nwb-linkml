"""
Manage the operation of nwb_linkml from environmental variables
"""

from typing import Optional, Literal
import tempfile
from pathlib import Path

from pydantic import (
    BaseModel,
    DirectoryPath,
    Field,
    FieldValidationInfo,
    computed_field,
    field_validator,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

LOG_LEVELS = Literal["DEBUG", "INFO", "WARNING", "ERROR"]


class LogConfig(BaseModel):
    """
    Configuration for logging
    """

    level: LOG_LEVELS = "INFO"
    """
    Severity of log messages to process.
    """
    level_file: Optional[LOG_LEVELS] = None
    """
    Severity for file-based logging. If unset, use ``level``
    """
    level_stdout: Optional[LOG_LEVELS] = "WARNING"
    """
    Severity for stream-based logging. If unset, use ``level``
    """
    file_n: int = 5
    """
    Number of log files to rotate through
    """
    file_size: int = 2**22  # roughly 4MB
    """
    Maximum size of log files (bytes)
    """

    @field_validator("level", "level_file", "level_stdout", mode="before")
    @classmethod
    def uppercase_levels(cls, value: Optional[str] = None) -> Optional[str]:
        """
        Ensure log level strings are uppercased
        """
        if value is not None:
            value = value.upper()
        return value

    @model_validator(mode="after")
    def inherit_base_level(self) -> "LogConfig":
        """
        If loglevels for specific output streams are unset, set from base :attr:`.level`
        """
        levels = ("level_file", "level_stdout")
        for level_name in levels:
            if getattr(self, level_name) is None:
                setattr(self, level_name, self.level)
        return self


class Config(BaseSettings):
    """
    Configuration for nwb_linkml, populated by default but can be overridden
    by environment variables.

    Nested models can be assigned from .env files with a __ (see examples)

    Examples:

        export NWB_LINKML_CACHE_DIR="/home/mycache/dir"
        export NWB_LINKML_LOGS__LEVEL="debug"

    """

    model_config = SettingsConfigDict(env_prefix="nwb_linkml_")
    cache_dir: DirectoryPath = Field(
        default_factory=lambda: Path(tempfile.gettempdir()) / "nwb_linkml__cache",
        description="Location to cache generated schema and models",
    )
    log_dir: Path = Field(
        Path("logs"),
        description="Location to store logs. If a relative directory, relative to ``cache_dir``",
    )
    logs: LogConfig = Field(LogConfig(), description="Log configuration")

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
        """
        The base cache dir should exist before validating other paths
        """
        v = Path(v)
        v.mkdir(exist_ok=True)
        assert v.exists()
        return v

    @model_validator(mode="after")
    def log_dir_relative_to_cache_dir(self) -> "Config":
        """
        If log dir is relative, put it beneath the cache_dir
        """
        if not self.log_dir.is_absolute():
            self.log_dir = self.cache_dir / self.log_dir
        return self

    @model_validator(mode="after")
    def folders_exist(self) -> "Config":
        """
        All folders, including computed folders, should exist.
        """
        for path in self.model_dump().values():
            if isinstance(path, Path):
                path.mkdir(exist_ok=True, parents=True)
                assert path.exists()
        return self

    def __post_init__(self):
        self.cache_dir.mkdir(exist_ok=True)
        self.linkml_dir.mkdir(exist_ok=True)
        self.pydantic_dir.mkdir(exist_ok=True)
        self.git_dir.mkdir(exist_ok=True)
