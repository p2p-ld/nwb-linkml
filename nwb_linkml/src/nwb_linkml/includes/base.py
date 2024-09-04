"""
Modifications to the ConfiguredBaseModel used by all generated classes
"""

BASEMODEL_GETITEM = """
    def __getitem__(self, val: Union[int, slice]) -> Any:
        \"\"\"Try and get a value from value or "data" if we have it\"\"\"
        if hasattr(self, "value") and self.value is not None:
            return self.value[val]
        elif hasattr(self, "data") and self.data is not None:
            return self.data[val]
        else:
            raise KeyError("No value or data field to index from")
"""

BASEMODEL_COERCE_VALUE = """
    @field_validator("*", mode="wrap")
    @classmethod
    def coerce_value(cls, v: Any, handler) -> Any:
        \"\"\"Try to rescue instantiation by using the value field\"\"\"
        try:
            return handler(v)
        except Exception as e1:
            try:
                return handler(v.value)
            except:
                raise e1
"""

BASEMODEL_COERCE_CHILD = """
    @field_validator("*", mode="before")
    @classmethod
    def coerce_subclass(cls, v: Any, info) -> Any:
        \"\"\"Recast parent classes into child classes\"\"\"
        return v
        pdb.set_trace()
"""
