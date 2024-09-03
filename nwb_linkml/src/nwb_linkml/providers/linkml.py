"""
Provider for LinkML schema built from NWB schema
"""

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from linkml_runtime import SchemaView
from linkml_runtime.dumpers import yaml_dumper
from linkml_runtime.linkml_model import SchemaDefinition, SchemaDefinitionName

from nwb_linkml import adapters, io
from nwb_linkml.adapters import BuildResult
from nwb_linkml.maps.naming import relative_path
from nwb_linkml.providers import Provider
from nwb_linkml.providers.git import DEFAULT_REPOS
from nwb_linkml.ui import AdapterProgress
from nwb_schema_language import Namespaces


@dataclass
class LinkMLSchemaBuild:
    """Build result from :meth:`.LinkMLProvider.build`"""

    version: str
    namespace: Path
    name: str
    result: Optional[BuildResult]


class LinkMLProvider(Provider):
    """
    Provider for conversions from nwb schema language to linkML.

    By default, generate and manage a nest of temporary cache directories
    (as configured by :class:`.Config`) for each version of a given namespace.

    Like other :class:`.Provider` classes, this model is not a singleton but
    behaves a bit like one in that when instantiated without arguments
    it is stateless (except for configuration by environment-level variables).
    So we don't use ``@classmethod`` s here, but instantiating the class should remain
    cheap.

    Namespaces can be built from:

    * namespace .yaml files: :meth:`.build_from_yaml`
    * dictionaries, as are usually packaged in nwb files: :meth:`.build_from_dicts`

    All of which feed into...

    * :class:`~.adapters.NamespacesAdapter` used throughout the rest of ``nwb_linkml`` -
      :meth:`.build`

    After a namespace is built, it can be accessed using :meth:`.LinkMLProvider.get`, which
    can also be consumed by other providers, so a given namespace and version should only need
    to be built once.

    Note:
        At the moment there is no checking (eg. by comparing hashes) of different sources that
        purport to be a given version of a namespace. When ambiguous, the class prefers to
        build sets of namespaces together and use the most recently built ones since there is no
        formal system for linking versions of namespaced schemas in nwb schema language.

    Examples:

        .. code-block:: python

            provider = LinkMLProvider()
            # Simplest case, get the core nwb schema from the default NWB core repo
            core = provider.get('core')
            # Get a specific version of the core schema
            core_other_version = provider.get('core', '2.2.0')
            # Build a custom schema and then get it
            # provider.build_from_yaml('myschema.yaml')
            # my_schema = provider.get('myschema')

    """

    PROVIDES = "linkml"
    PROVIDES_CLASS = SchemaDefinition

    @property
    def path(self) -> Path:
        """``linkml_dir`` provided by :class:`.Config`"""
        return self.config.linkml_dir

    def build_from_yaml(
        self, path: Path, **kwargs: dict
    ) -> Dict[str | SchemaDefinitionName, LinkMLSchemaBuild]:
        """
        Build a namespace's schema

        Arguments:
            path (:class:`pathlib.Path`): Path to the namespace .yaml
            kwargs: passed to :meth:`.build`
        """
        ns_adapter = adapters.NamespacesAdapter.from_yaml(path)
        return self.build(ns_adapter, **kwargs)

    def build_from_dicts(
        self, schemas: Dict[str, dict], **kwargs: dict
    ) -> Dict[str | SchemaDefinitionName, LinkMLSchemaBuild]:
        """
        Build from schema dictionaries, eg. as come from nwb files

        Arguments:
            schemas (dict): A dictionary of ``{'schema_name': {:schema_definition}}``.
                The "namespace" schema should have the key ``namespace``, which is used
                to infer version and schema name. Post-load maps should have already
                been applied
        """
        ns_adapters = {}
        for ns_name, ns_schemas in schemas.items():
            ns = Namespaces(**ns_schemas["namespace"])
            typed_schemas = [
                io.schema.load_schema_file(path=Path(key + ".yaml"), yaml=val)
                for key, val in ns_schemas.items()
                if key != "namespace"
            ]
            ns_adapter = adapters.NamespacesAdapter(namespaces=ns, schemas=typed_schemas)
            ns_adapters[ns_name] = ns_adapter

        # get the correct imports
        for adapter in ns_adapters.values():
            for schema_needs in adapter.needed_imports.values():
                for needed in schema_needs:
                    adapter.imported.append(ns_adapters[needed])
            adapter.populate_imports()

        # then do the build
        res = {}
        for adapter in ns_adapters.values():
            res.update(self.build(adapter, **kwargs))

        return res

    def build(
        self,
        ns_adapter: adapters.NamespacesAdapter,
        versions: Optional[dict] = None,
        dump: bool = True,
        force: bool = False,
    ) -> Dict[str | SchemaDefinitionName, LinkMLSchemaBuild]:
        """
        Arguments:
            namespaces (:class:`.NamespacesAdapter`): Adapter
                (populated with any necessary imported namespaces) to build
            versions (dict): Dict of specific versions to use
                for cross-namespace imports. as ``{'namespace': 'version'}``
                If none is provided, use the most recent version
                available.
            dump (bool): If ``True`` (default), dump generated schema to YAML. otherwise just return
            force (bool): If ``False`` (default), don't build schema that already exist.
                If ``True`` , clear directory and rebuild

        Returns:
            Dict[str, LinkMLSchemaBuild]. For normal builds,
            :attr:`.LinkMLSchemaBuild.result` will be populated with results
            of the build. If ``force == False`` and the schema already exist, it will be ``None``
        """

        # Return cached result if available
        if not force and all(
            [
                (self.namespace_path(ns, version) / "namespace.yaml").exists()
                for ns, version in ns_adapter.versions.items()
            ]
        ):
            return {
                k: LinkMLSchemaBuild(
                    name=k,
                    result=None,
                    namespace=self.namespace_path(k, v) / "namespace.yaml",
                    version=v,
                )
                for k, v in ns_adapter.versions.items()
            }

        if self.verbose:
            progress = AdapterProgress(ns_adapter)
            with progress:
                built = ns_adapter.build(progress=progress)
        else:
            built = ns_adapter.build()

        # write schemas to yaml files
        build_result = {}

        namespace_sch = [
            sch
            for sch in built.schemas
            if "is_namespace" in sch.annotations
            and sch.annotations["is_namespace"].value in ("True", True)
        ]
        for ns_linkml in namespace_sch:
            version = ns_adapter.versions[ns_linkml.name]

            # prepare the output directory
            version_path = self.namespace_path(ns_linkml.name, version, allow_repo=False)
            if version_path.exists() and force:
                shutil.rmtree(str(version_path))
            version_path.mkdir(exist_ok=True, parents=True)
            ns_file = version_path / "namespace.yaml"

            # schema built as part of this namespace that aren't the namespace file
            other_schema = [
                sch
                for sch in built.schemas
                if sch.name.split(".")[0] == ns_linkml.name and sch not in namespace_sch
            ]

            if force or not ns_file.exists():
                ns_linkml = self._fix_schema_imports(ns_linkml, ns_adapter, ns_file)
                yaml_dumper.dump(ns_linkml, ns_file)

                # write the schemas for this namespace
                for sch in other_schema:
                    output_file = version_path / (sch.name + ".yaml")
                    # fix the paths for intra-schema imports
                    sch = self._fix_schema_imports(sch, ns_adapter, output_file)
                    yaml_dumper.dump(sch, output_file)

            # make return result for just this namespace
            build_result[ns_linkml.name] = LinkMLSchemaBuild(
                namespace=ns_file,
                name=ns_linkml.name,
                result=BuildResult(schemas=[ns_linkml, *other_schema]),
                version=version,
            )

        return build_result

    def _fix_schema_imports(
        self, sch: SchemaDefinition, ns_adapter: adapters.NamespacesAdapter, output_file: Path
    ) -> SchemaDefinition:
        """
        Look there are a lot of nested directories around here and they aren't necessarily
        all available at generation time. We have to relink relative imports between schema as
        they are split and generated from the NWB.
        """
        for animport in sch.imports:
            if animport.split(".")[0] in ns_adapter.versions:
                imported_path = (
                    self.namespace_path(
                        animport.split(".")[0], ns_adapter.versions[animport.split(".")[0]]
                    )
                    / "namespace"
                )
                rel_path = relative_path(imported_path, output_file)
                if str(rel_path) == "." or str(rel_path) == "namespace":
                    # same directory, just keep the existing import
                    continue
                idx = sch.imports.index(animport)
                del sch.imports[idx]
                sch.imports.insert(idx, str(rel_path))
        return sch

    def get(self, namespace: str, version: Optional[str] = None) -> SchemaView:
        """
        Get a schema view over the namespace.

        If a matching path for the namespace and version exists in the :attr:`.path`,
        then return the SchemaView over that namespace.

        Otherwise, try and find a source using our :data:`.providers.git.DEFAULT_REPOS`.

        If none is found, then you need to build and cache the (probably custom) schema first with
        :meth:`.build`
        """
        path = self.namespace_path(namespace, version) / "namespace.yaml"
        if not path.exists():
            path = self._find_source(namespace, version)
        sv = SchemaView(path)
        sv.path = path
        return sv

    def _find_source(self, namespace: str, version: Optional[str] = None) -> Path:
        """Try and find the namespace if it exists in our default repository and build it!"""
        ns_repo = DEFAULT_REPOS.get(namespace, None)
        if ns_repo is None:
            raise KeyError(
                f"Namespace {namespace} could not be found, and no git repository source has been"
                " configured!"
            )
        ns_file = ns_repo.provide_from_git(commit=version)
        res = self.build_from_yaml(ns_file)
        return res[namespace].namespace
