"""
Special types for mimicking HDMF special case behavior
"""

from typing import Optional
from pydantic import BaseModel, field_validator, ConfigDict, model_validator


class DynamicTableMixin(BaseModel):
    model_config = ConfigDict(extra='allow')

    @model_validator(mode='after')
    def ensure_equal_length(cls, model: 'DynamicTableMixin') -> 'DynamicTableMixin':
        """
        Ensure all vectors are of equal length
        """
        raise NotImplementedError('TODO')

    @model_validator(mode="after")
    def create_index_backrefs(cls, model: 'DynamicTableMixin') -> 'DynamicTableMixin':
        """
        Ensure that vectordata with vectorindexes know about them
        """
        raise NotImplementedError('TODO')

    def __getitem__(self, item):
        raise NotImplementedError('TODO')

    def __setitem__(self, key, value):
        raise NotImplementedError('TODO')



class VectorDataMixin(BaseModel):
    index: Optional[BaseModel] = None


