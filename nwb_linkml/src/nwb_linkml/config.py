"""
Manage the operation of nwb_linkml from environmental variables
"""
import tempfile
from pathlib import Path
from pydantic import Field, DirectoryPath, computed_field, field_validator, FieldValidationInfo
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
        default_factory= lambda: Path(tempfile.gettempdir()) / 'nwb_linkml__cache',
        description="Location to cache generated schema and models")

    @computed_field
    @property
    def linkml_dir(self) -> Path:
        """Directory to store generated linkml models"""
        return self.cache_dir / 'linkml'

    @computed_field
    @property
    def pydantic_dir(self) -> Path:
        """Directory to store generated pydantic models"""
        return self.cache_dir / 'pydantic'


    @field_validator('cache_dir', mode='before')
    @classmethod
    def folder_exists(cls, v: Path, info: FieldValidationInfo) -> Path:
        v = Path(v)
        v.mkdir(exist_ok=True)
        assert v.exists()
        return v

    def __post_init__(self):
        self.cache_dir.mkdir(exist_ok=True)
        self.linkml_dir.mkdir(exist_ok=True)
        self.pydantic_dir.mkdir(exist_ok=True)


