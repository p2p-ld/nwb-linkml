import shutil
import sys
from pathlib import Path
from typing import Optional

import pytest
from nptyping import Shape, UByte
from numpydantic import NDArray

import nwb_linkml
from nwb_linkml.maps.naming import version_module_case
from nwb_linkml.providers import LinkMLProvider, PydanticProvider
from nwb_linkml.providers.git import DEFAULT_REPOS

CORE_MODULES = (
    "core.nwb.base",
    "core.nwb.device",
    "core.nwb.epoch",
    "core.nwb.image",
    "core.nwb.file",
    "core.nwb.misc",
    "core.nwb.behavior",
    "core.nwb.ecephys",
    "core.nwb.icephys",
    "core.nwb.ogen",
    "core.nwb.ophys",
    "core.nwb.retinotopy",
    "core.nwb.language",
)


@pytest.mark.parametrize(
    ["repo_version", "schema_version", "schema_dir"], [("2.6.0", "2.6.0-alpha", "v2_6_0_alpha")]
)
def test_linkml_provider(tmp_output_dir, repo_version, schema_version, schema_dir):

    provider = LinkMLProvider(path=tmp_output_dir, allow_repo=False)
    # clear any prior output
    shutil.rmtree(provider.path)
    assert not provider.path.exists()
    assert not (provider.namespace_path("core", repo_version) / "namespace.yaml").exists()

    # end to end, check that we can get the 'core' repo at the latest version
    # in the gitrepo
    core = provider.get("core", version=repo_version)

    assert core.schema.version == schema_version
    assert all([mod in core.schema.imports for mod in CORE_MODULES])
    assert schema_dir in [path.name for path in (provider.path / "core").iterdir()]


@pytest.mark.skip()
def test_linkml_build_from_yaml(tmp_output_dir):
    core = DEFAULT_REPOS["core"]
    git_dir = nwb_linkml.Config().git_dir / "core"
    if git_dir.exists():
        shutil.rmtree(str(git_dir))
    ns_file = core.provide_from_git("2.6.0")
    assert git_dir.exists()
    assert ns_file.exists()

    provider = LinkMLProvider(path=tmp_output_dir, allow_repo=False)

    res = provider.build_from_yaml(ns_file)


# @pytest.mark.depends(on=["test_linkml_provider"])
@pytest.mark.xfail
@pytest.mark.parametrize(
    ["class_name", "test_fields"],
    [
        (
            "TimeSeries",
            {
                "name": str,
                "description": Optional[str],
                "comments": Optional[str],
                "data": "TimeSeriesData",
                "timestamps": "Optional",  # __name__ just gets the first part of Optional[TimeSeriesTimestamps]
                "control": Optional[NDArray[Shape["* num_times"], UByte]],
            },
        )
    ],
)
def test_pydantic_provider_core(tmp_output_dir, class_name, test_fields):
    provider = PydanticProvider(path=tmp_output_dir)
    # clear any prior output
    assert provider.path.parent == tmp_output_dir
    shutil.rmtree(provider.path, ignore_errors=True)
    assert not provider.path.exists()

    # first, we should not build if we're allowed to get core from repo
    core = provider.get("core", allow_repo=True)
    assert Path(nwb_linkml.__file__).parent in Path(core.__file__).parents
    assert not (provider.path / "core").exists()

    # then, if we're not allowed to get repo versions, we build!
    del sys.modules[core.__name__]
    core = provider.get("core", allow_repo=False)
    # ensure we didn't get the builtin one
    assert Path(nwb_linkml.__file__).parent not in Path(core.__file__).parents
    namespace_path = (
        tmp_output_dir / "pydantic" / "core" / version_module_case(core.version) / "namespace.py"
    )
    assert namespace_path.exists()
    assert Path(core.__file__) == namespace_path

    test_class = getattr(core, class_name)
    assert test_class == provider.get_class("core", class_name)

    for k, v in test_fields.items():
        if isinstance(v, str):
            assert test_class.model_fields[k].annotation.__name__ == v
        else:
            assert test_class.model_fields[k].annotation == v
