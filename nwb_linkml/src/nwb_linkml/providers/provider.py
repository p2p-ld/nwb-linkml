import importlib
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, TypeVar

from nwb_linkml import Config
from nwb_linkml.maps.naming import module_case, version_module_case

P = TypeVar("P")


class Provider(ABC):
    """
    Metaclass for different kind of providers!

    Args:
        path (:class:`pathlib.Path`): Override the temporary directory configured by
            the environment-wide :class:`.Config` object as the base directory that the
            subclasses provide to.
        verbose (bool): If ``True``, print things like progress bars to stdout :)

    Attributes:
        config (:class:`.Config`): Configuration for the directories used by this
            provider, unless overridden by ``path``
        allow_repo (bool): Allow the pathfinder to return the installed repository/package,
            useful to enforce building into temporary directories, decoupling finding a path
            during loading vs. building. Building into the repo is still possible if both
            namespace and version are provided (ie. the path is fully qualified) and
            :attr:`.config`'s path is the repository path.
        cache_dir (:class:`pathlib.Path`): The main cache directory under which the other
            providers will store the things they provide
    """

    PROVIDES: str
    PROVIDES_CLASS: P = None

    def __init__(self, path: Optional[Path] = None, allow_repo: bool = True, verbose: bool = True):
        config = Config(cache_dir=path) if path is not None else Config()
        self.config = config
        self.cache_dir = config.cache_dir
        self.allow_repo = allow_repo
        self.verbose = verbose

    @property
    @abstractmethod
    def path(self) -> Path:
        """
        Base path for this kind of provider
        """

    @abstractmethod
    def build(self, *args: Any) -> P:
        """
        Whatever needs to be done to build this thing, if applicable
        """

    @abstractmethod
    def get(self, *args: Any) -> Any:
        """
        Get a cached item.

        Optionally, try any build it if it's possible to do so
        """

    def namespace_path(
        self, namespace: str, version: Optional[str] = None, allow_repo: Optional[bool] = None
    ) -> Path:
        """
        Get the location for a given namespace of this type.

        Note that we don't check for existence, because this method should
        also be used when generating schema --- this is the canonical location

        Arguments:
            namespace (str): Namespace to get!
            version (str): Optional, version of namespace. If ``None``,
                either get the most recent version built, or if
                ``namespace`` is ``core`` or ``hdmf-common``, use the
                modules provided with the package. We do not use the most
                recent *version*, but the most recently *generated* version
                because it's assumed that's the one you want if you're just
                gesturally reaching for one.
            allow_repo (bool): Optional - override instance-level ``allow_repo`` attr
        """
        if allow_repo is None:
            allow_repo = self.allow_repo

        namespace_module = module_case(namespace)
        namespace_path = self.path / namespace_module
        if not namespace_path.exists() and namespace in ("core", "hdmf-common") and allow_repo:
            # return builtins
            module_path = Path(importlib.util.find_spec("nwb_linkml").origin).parent

            if self.PROVIDES == "linkml":
                namespace_path = module_path / "schema" / "linkml" / namespace
            elif self.PROVIDES == "pydantic":
                namespace_path = module_path / "models" / "pydantic" / namespace

        if version is not None:
            version_path = namespace_path / version_module_case(version)
            # version_path.mkdir(exist_ok=True, parents=True)
        else:
            # or find the most recently built one
            versions = sorted(namespace_path.iterdir(), key=os.path.getmtime)
            versions = [v for v in versions if v.is_dir() and v.name not in ("__pycache__")]
            if len(versions) == 0:
                raise FileNotFoundError("No version provided, and no existing schema found")
            version_path = versions[-1]

        return version_path

    @property
    def available_versions(self) -> Dict[str, List[str]]:
        """
        Dictionary mapping a namespace to a list of built versions
        """
        from nwb_linkml.providers import LinkMLProvider
        versions = {}  # type: Dict[str, List[Path]]

        # first get any builtins provided by the package itself
        # these get overwritten by
        module_path = Path(importlib.util.find_spec("nwb_linkml").origin).parent
        builtin_namespaces = []
        if self.PROVIDES == "linkml":
            namespace_path = module_path / "schema" / "linkml"
            builtin_namespaces = list(namespace_path.iterdir())
        elif self.PROVIDES == "pydantic":
            namespace_path = module_path / "models" / "pydantic"
            builtin_namespaces = list(namespace_path.iterdir())

        tmp_paths = []
        try:
            tmp_paths.extend(list(self.path.iterdir()))
            if self.PROVIDES == "pydantic":
                # we also include versions that we just have the linkml version of
                # because they are also available, we just have to build them.
                # maybe the semantics of this property are getting overloaded tho
                # and we need to separate the maintenance of the temporary directory
                # from providing from it
                tmp_paths.extend(list(LinkMLProvider(path=self.config.cache_dir).path.iterdir()))
        except FileNotFoundError:
            # fine, just return the builtins
            pass

        for ns_dir in builtin_namespaces + tmp_paths:
            if not ns_dir.is_dir():
                continue
            if ns_dir.name not in versions:
                versions[ns_dir.name] = []

            versions[ns_dir.name].extend([v for v in ns_dir.iterdir() if v.is_dir()])

        # flatten out in case we got duplicates between the builtins and cache
        res = {
            k: [
                v.name for v in sorted(set(v_paths), key=os.path.getmtime) if v.name.startswith("v")
            ]
            for k, v_paths in versions.items()
        }
        return res


