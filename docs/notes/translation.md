# translation

what operations do we need when translating between schema languages?

- Iteration - control over "for what" in the source or target domain.
  eg. we need to map "all attributes and properties to slots" but then the
  other direction of selection where we need to do one of everything per item
  in the source domain as well
- dependence - source and target domain have different notions of linking
- level shifting - need to translate when something is a language-level
  item to a schema-level item/object/class



Steps:
- each namespaces or schema object creates one linkml schema file
- namespaces: one map, just imports all the other schema
- schema: actually create the object in the schema.
  - Classes:
    - Groups
    - Enums (see below)
  - Slots
    - Attributes
- new files: files not in the source domain
  - enum classes

- Rename items