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
                if hasattr(v, "value"):
                    return handler(v.value)
                else:
                    return handler(v["value"])
            except Exception as e2:
                raise e2 from e1
"""
