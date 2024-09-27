"""
Modifications to the ConfiguredBaseModel used by all generated classes
"""

BASEMODEL_GETITEM = """
    def __getitem__(self, val: Union[int, slice, str]) -> Any:
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
    def coerce_value(cls, v: Any, handler, info) -> Any:
        \"\"\"Try to rescue instantiation by using the value field\"\"\"
        try:
            return handler(v)
        except Exception as e1:
            try:
                return handler(v.value)
            except AttributeError:
                try:
                    return handler(v["value"])
                except (IndexError, KeyError, TypeError):
                    raise e1
"""

BASEMODEL_CAST_WITH_VALUE = """
    @field_validator("*", mode="wrap")
    @classmethod
    def cast_with_value(cls, v: Any, handler, info) -> Any:
        \"\"\"Try to rescue instantiation by casting into the model's value field\"\"\"
        try:
            return handler(v)
        except Exception as e1:
            try:
                return handler({"value": v})
            except Exception:
                raise e1
"""

BASEMODEL_COERCE_CHILD = """
    @field_validator("*", mode="before")
    @classmethod
    def coerce_subclass(cls, v: Any, info) -> Any:
        \"\"\"Recast parent classes into child classes\"\"\"
        if isinstance(v, BaseModel):
            annotation = cls.model_fields[info.field_name].annotation
            while hasattr(annotation, "__args__"):
                annotation = annotation.__args__[0]
            try:
                if issubclass(annotation, type(v)) and annotation is not type(v):
                    if v.__pydantic_extra__:
                        v = annotation(**{**v.__dict__, **v.__pydantic_extra__})
                    else:
                        v = annotation(**v.__dict__)            
            except TypeError:
                # fine, annotation is a non-class type like a TypeVar
                pass
        return v
"""

BASEMODEL_EXTRA_TO_VALUE = """
    @model_validator(mode="before")
    @classmethod
    def gather_extra_to_value(cls, v: Any) -> Any:
        \"\"\"
        For classes that don't allow extra fields and have a value slot,
        pack those extra kwargs into ``value``
        \"\"\"
        if (
            cls.model_config["extra"] == "forbid" 
            and "value" in cls.model_fields 
            and isinstance(v, dict)
        ):
            extras = {key:val for key,val in v.items() if key not in cls.model_fields}
            if extras:
                for k in extras:
                    del v[k]
                if "value" in v:
                    v["value"].update(extras)
                else:
                    v["value"] = extras
        return v
"""

BASEMODEL_SERIALIZER = """
    @model_serializer(mode="wrap", when_used="json")
    def serialize_model(self, nxt, info) -> Dict[str, Any]:
        try:
            return nxt(self, info)
        except Exception as e:
            return {"ERROR":str(e), "TYPE": str(type(self))}
            if 'Circular reference' in str(e):
                return {"REFERENCE":"REFERENCE"}
            pdb.set_trace()
            json_dump_fields = ('indent', 'include', 'exclude', 'context', 'by_alias', 'exclude_unset', 'exclude_defaults', 'exclude_none', 'round_trip', 'warnings', 'serialize_as_any')
            return self.model_dump_json(**{k:v for k,v in info.__dict__.items() if k in json_dump_fields})
"""
