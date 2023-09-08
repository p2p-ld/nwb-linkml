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


## Translation choices

We aren't doing a 1:1 translation of NWB! The goal is to make something that is *import*
backwards-compatible - ie. we can read NWB traditional nwb files - but not necessarily
*export* for now. We will get to that eventually. NWB as it is now is highly tied to hdf5
in multiple places - from the hdmf-common namespace to the nwb file classes, 
we want to instead abstract the structure of NWB so the schema can be used
as a programming element (ie. labs can write their own schema extensions in yaml, 
generate pydantic modules for them, and they should Just Work TM) with various different
storage backends. 

- Don't try and emulate the nwb.file schema - it is basically a file layout that indicates
  what should go where. We are moving I/O out of the schema: storage layout is at a different level than the schema
- Don't worry about most of hdmf-common: instead create sensible generics that can be implemented in different ways by different storage mediums