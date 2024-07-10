"""
Class for managing, building, and caching built schemas.

The nwb.core and hdmf-common schema are statically built and stored in this repository,
but to make it feasible to use arbitrary schema, eg. those stored inside of
an NWB file, we need a bit of infrastructure for generating and caching
pydantic models on the fly.

Relationship to other modules:
* :mod:`.adapters` manage the conversion from NWB schema language to linkML.
* :mod:`.generators` create models like pydantic models from the linkML schema
* :mod:`.providers` then use ``adapters`` and ``generators``
  to provide models from generated schema!

Providers create a set of directories with namespaces and versions,
so eg. for the linkML and pydantic providers:

.. code-block:: yaml

    cache_dir
      - linkml
        - nwb_core
          - v0_2_0
            - namespace.yaml
            - nwb.core.file.yaml
            - ...
          - v0_2_1
            - namespace.yaml
            - ...
        - my_schema
          - v0_1_0
            - ...
      - pydantic
        - nwb_core
          - v0_2_0
            - namespace.py
            - ...
          - v0_2_1
            - namespace.py
            - ...


"""

from pathlib import Path
from types import ModuleType
from typing import Dict, Optional, Type

from pydantic import BaseModel

from nwb_linkml import adapters
from nwb_linkml.providers import LinkMLProvider, Provider, PydanticProvider


class SchemaProvider(Provider):
    """
    Class to manage building and caching linkml and pydantic models generated
    from nwb schema language. Combines :class:`.LinkMLProvider` and :class:`.PydanticProvider`

    Behaves like a singleton without needing to be one - since we're working off
    caches on disk that are indexed by hash in most "normal" conditions you should
    be able to use this anywhere, though no file-level locks are present to ensure
    consistency.

    Store each generated schema in a directory structure indexed by
    schema namespace name and version
    """

    build_from_yaml = LinkMLProvider.build_from_yaml
    """
    Alias for :meth:`.LinkMLProvider.build_from_yaml` that also builds a pydantic model
    """
    build_from_dicts = LinkMLProvider.build_from_dicts
    """
    Alias for :meth:`.LinkMLProvider.build_from_dicts` that also builds a pydantic model
    """

    def __init__(self, versions: Optional[Dict[str, str]] = None, **kwargs):
        """
        Args:
            versions (dict): Dictionary like ``{'namespace': 'v1.0.0'}``
                used to specify that this provider should always
                return models from a specific version of a namespace
                (unless explicitly requested otherwise in a call to :meth:`.get` ).
            **kwargs: passed to superclass __init__ (see :class:`.Provider` )
        """
        self.versions = versions
        super().__init__(**kwargs)

    @property
    def path(self) -> Path:
        """``cache_dir`` provided by :class:`.Config`"""
        return self.config.cache_dir

    def build(
        self,
        ns_adapter: adapters.NamespacesAdapter,
        verbose: bool = True,
        linkml_kwargs: Optional[dict] = None,
        pydantic_kwargs: Optional[dict] = None,
        **kwargs,
    ) -> Dict[str, str]:
        """
        Build a namespace, storing its linkML and pydantic models.

        Args:
            ns_adapter:
            verbose (bool): If ``True`` (default), show progress bars
            linkml_kwargs (Optional[dict]): Dictionary of kwargs optionally passed to
                :meth:`.LinkMLProvider.build`
            pydantic_kwargs (Optional[dict]): Dictionary of kwargs optionally passed to
                :meth:`.PydanticProvider.build`
            **kwargs: Common options added to both ``linkml_kwargs`` and ``pydantic_kwargs``

        Returns:
            Dict[str,str] mapping namespaces to built pydantic sources
        """
        if linkml_kwargs is None:
            linkml_kwargs = {}
        if pydantic_kwargs is None:
            pydantic_kwargs = {}
        linkml_kwargs.update(kwargs)
        pydantic_kwargs.update(kwargs)

        linkml_provider = LinkMLProvider(path=self.path, verbose=verbose)
        pydantic_provider = PydanticProvider(path=self.path, verbose=verbose)

        linkml_res = linkml_provider.build(
            ns_adapter=ns_adapter, versions=self.versions, **linkml_kwargs
        )
        results = {}
        for ns, ns_result in linkml_res.items():
            results[ns] = pydantic_provider.build(
                ns_result["namespace"], versions=self.versions, **pydantic_kwargs
            )
        return results

    def get(self, namespace: str, version: Optional[str] = None) -> ModuleType:
        """
        Get a built pydantic model for a given namespace and version.

        Wrapper around :meth:`.PydanticProvider.get`
        """
        if version is None and self.versions is not None:
            version = self.versions.get(namespace, None)

        return PydanticProvider(path=self.path).get(namespace, version)

    def get_class(
        self, namespace: str, class_: str, version: Optional[str] = None
    ) -> Type[BaseModel]:
        """
        Get a pydantic model class from a given namespace and version!

        Wrapper around :meth:`.PydanticProvider.get_class`
        """
        if version is None and self.versions is not None:
            version = self.versions.get(namespace, None)

        return PydanticProvider(path=self.path).get_class(namespace, class_, version)
