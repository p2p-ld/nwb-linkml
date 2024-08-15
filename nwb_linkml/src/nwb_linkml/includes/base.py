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
