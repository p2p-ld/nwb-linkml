import pytest
import shutil

import yaml
from nwb_linkml.providers.git import GitRepo, NWB_CORE_REPO, HDMF_COMMON_REPO
from nwb_schema_language import Namespaces

@pytest.mark.parametrize(
    ['source', 'commit'],
    [
        (NWB_CORE_REPO, '761a0d7838304864643f8bc3ab88c93bfd437f2a'),
        (HDMF_COMMON_REPO, '660b6ac0780dd9d2cb1e56fea8b62c671ca5e2c8')
    ]
)
def test_gitrepo(source, commit):
    """
    Basic functionality of GitRepo
    """
    repo = GitRepo(source)

    # make a temp directory that exists
    first_dir = repo.temp_directory
    assert repo.temp_directory.exists()

    # find the same repository when it's deleted
    shutil.rmtree(str(repo.temp_directory))
    repo._temp_directory = None
    second_dir = repo.temp_directory
    assert first_dir == second_dir

    # successfully clone the repository after its deleted
    assert not any(repo.temp_directory.iterdir())
    repo.clone()
    # check that the namespace file exists and has some expected fields
    assert repo.namespace_file.exists()
    with open(repo.namespace_file, 'r') as nsfile:
        ns = yaml.safe_load(nsfile)
    # correct model instantiation confirms the repo was cloned successfully
    ns_model = Namespaces(**ns)

    # setting commit should change the active commit
    prior_commit = repo.active_commit
    repo.commit = commit
    assert prior_commit != repo.active_commit
    assert repo.active_commit == commit
    assert repo.commit == commit

    # remote is gotten correctly
    assert repo.remote == str(source.repository)

    # cleanup should remove files
    repo.cleanup()
    assert not any(repo.temp_directory.iterdir())

@pytest.mark.parametrize(
    ['source', 'commit'],
    [
        (NWB_CORE_REPO, 'b4f8838cbfbb7f8a117bd7e0aad19133d26868b4')
    ]
)
def test_gitrepo_check(source, commit):
    """
    Our check method should flag common problems with the repo
    """
    repo = GitRepo(NWB_CORE_REPO, commit=commit)
    # cleanup is tested separately
    repo.cleanup()

    # check should fail without warning when the repo is empty
    assert not repo.check()

    repo.clone()
    assert repo.check()

    # check should not warn but get us to the correct commit
    assert repo.active_commit == commit
    repo._git_call('checkout', 'HEAD~10')
    assert repo.active_commit != commit
    # check should pass but switch to proper commit
    assert repo.check()
    assert repo.active_commit == commit

    # check should fail on repo namespace mismatch
    old_repo = repo.namespace.repository
    repo.namespace.repository = "https://example.com/a/git/repository"
    with pytest.warns(UserWarning, match='.*wrong remote.*'):
        assert not repo.check()
    repo.namespace.repository = old_repo
    assert repo.check()



