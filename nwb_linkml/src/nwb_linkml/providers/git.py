"""
Define and manage NWB namespaces in external repositories
"""
import pdb
from typing import Optional, Dict, List
import warnings
from pathlib import Path
import tempfile
import subprocess
import shutil

from pydantic import BaseModel, HttpUrl, FilePath, DirectoryPath, Field

from nwb_linkml.config import Config

class NamespaceRepo(BaseModel):
    """
    Definition of one NWB namespaces file to import from a git repository
    """
    name: str = Field(description="Short name used to refer to this namespace (usually equivalent to the name field within a namespaces NWB list)")
    repository: HttpUrl | DirectoryPath = Field(description="URL or local absolute path to the root repository")
    path: Path = Field(description="Relative path from the repository root to the namespace file")
    versions: List[str] = Field(
        description="Known versions for this namespace repository, correspond to commit hashes or git tags that can be checked out by :class:`.GitRepo`",
        default_factory=list
    )

    def provide_from_git(self, commit:str|None=None) -> Path:
        git = GitRepo(self, commit)
        git.clone()
        return git.namespace_file

# Constant namespaces
NWB_CORE_REPO = NamespaceRepo(
    name="core",
    repository="https://github.com/NeurodataWithoutBorders/nwb-schema",
    path=Path("core/nwb.namespace.yaml"),
    versions=["2.2.0", "2.2.1", "2.2.2", "2.2.4", "2.2.5", "2.3.0", "2.4.0", "2.5.0", "2.6.0"]
)

HDMF_COMMON_REPO = NamespaceRepo(
    name="hdmf-common",
    repository="https://github.com/hdmf-dev/hdmf-common-schema",
    path=Path("common/namespace.yaml"),
    versions=["1.1.0", "1.1.1", "1.1.2", "1.1.3", "1.2.0", "1.2.1", "1.3.0", "1.4.0", "1.5.0", "1.5.1", "1.6.0", "1.7.0", "1.8.0"]
)

DEFAULT_REPOS = {
    repo.name: repo for repo in [NWB_CORE_REPO, HDMF_COMMON_REPO]
}  # type: Dict[str, NamespaceRepo]


class GitError(OSError):
    pass

class GitRepo:
    """
    Manage a temporary git repository that provides the NWB yaml files
    """
    def __init__(
            self,
            namespace:NamespaceRepo,
            commit:str|None=None,
            path: Optional[Path] = None
    ):
        """
        Args:
            namespace (:class:`.NamespaceRepo`): The namespace repository to clone!
            commit (str): A specific commit or tag to check out
            path (:class:`pathlib.Path`): A directory to clone to - if ``None``, use :attr:`~.Config.git_dir` / :attr:`.NamespaceRepo.name`
        """
        self._temp_directory = path
        self.namespace = namespace
        self._commit = commit



    def _git_call(self, *args) -> subprocess.CompletedProcess:
        res = subprocess.run(
            ['git', '-C', self.temp_directory, *args],
            capture_output=True
        )
        if res.returncode != 0:
            raise GitError(f'Git call did not complete successfully.\n---\nCall: {args}\nResult: {res.stderr}')
        return res

    @property
    def temp_directory(self) -> Path:
        """
        Temporary directory where this repository will be cloned to
        """
        if self._temp_directory is None:
            git_dir = Config().git_dir
            self._temp_directory = git_dir / self.namespace.name
            if not self._temp_directory.exists():
                self._temp_directory.mkdir(parents=True)

        return self._temp_directory

    @property
    def remote(self) -> str:
        """
        URL for "origin" remote
        """
        res = self._git_call('remote', 'get-url', 'origin')
        return res.stdout.decode('utf-8').strip()

    @property
    def active_commit(self) -> str:
        """
        Currently checked out commit
        """
        res = self._git_call('rev-parse', 'HEAD')
        commit = res.stdout.decode('utf-8').strip()
        return commit

    @property
    def namespace_file(self) -> Path:
        """
        Local path to the indicated namespace file.
        """
        return self.temp_directory / self.namespace.path

    @property
    def commit(self) -> Optional[str]:
        """
        The intended commit to check out.

        If ``None``: if :attr:`NamespaceRepo.versions`, use the last version. Otherwise use ``HEAD``

        Should match :attr:`.active_commit`, differs semantically in that it is used to
        set the active_commit, while :attr:`.active_commit` reads what commit is actually checked out
        """
        return self._commit

    @commit.setter
    def commit(self, commit:str|None):
        # setting commit as None should do nothing if we have already cloned,
        # and if we are just cloning we will always be at the most recent commit anyway
        if commit is not None:
            # first get out of a potential detached head state
            # that would cause a call to "HEAD" to fail in unexpected ways
            if self.detached_head:
                self._git_call('checkout', self.default_branch)

            self._git_call('checkout', commit)

        self._git_call('submodule', 'update', '--init', '--recursive')
        self._commit = commit

    @property
    def tag(self) -> str:
        """
        Get/set the currently checked out repo tag.

        Returns:
            str: the result of ``git describe --tags``, which is
            equal to the tag if it is checked out, otherwise it is the tag
            plus some number of revisions and the short hash.

        Examples:

            >>> repo = GitRepo(NWB_CORE_REPO)
            >>> repo.clone()
            >>> # Check out a tag specifically
            >>> repo.tag = "2.6.0"
            >>> repo.tag
            '2.6.0'
            >>> # Now check out a commit some number after the tag.
            >>> repo.commit = "ec0a879"
            >>> repo.tag
            '2.6.0-5-gec0a879'

        """
        res =  self._git_call('describe', '--tags')
        return res.stdout.decode('utf-8').strip()

    @tag.setter
    def tag(self, tag:str):
        # first check that we have the most recent tags
        self._git_call('fetch', '--all', '--tags')
        self._git_call('checkout', f'tags/{tag}')
        # error will be raised by _git_call if tag not found
        self._git_call('submodule', 'update', '--init', '--recursive')

    @property
    def default_branch(self) -> str:
        """
        Default branch as configured for this repository

        Gotten from ``git symbolic-ref``
        """
        res = self._git_call('symbolic-ref', 'refs/remotes/origin/HEAD')
        return res.stdout.decode('utf-8').strip().split('/')[-1]

    @property
    def detached_head(self) -> bool:
        """
        Detect if repo is in detached HEAD state that might need to be undone before
        checking out eg. a HEAD commit.

        Returns:
            bool: ``True`` if in detached head mode, ``False`` otherwise
        """
        res = self._git_call('branch', '--show-current')
        branch = res.stdout.decode('utf-8').strip()
        if not branch:
            return True
        else:
            return False

    def check(self) -> bool:
        """
        Check if the repository is already cloned and checked out

        Returns:
            (bool) True if present, False if not
        """
        if not any(self.temp_directory.iterdir()):
            # directory is empty
            return False

        try:
            # check our commit, this also checks if we're a git repo
            if self.active_commit != self.commit and self.commit is not None:
                self.commit = self.commit

        except GitError:
            return False

        # Check that the remote matches
        if self.remote != str(self.namespace.repository):
            warnings.warn(f'Repository exists, but has the wrong remote URL.\nExpected: {self.namespace.repository}\nGot:{self.remote.strip(".git")}')
            return False

        # otherwise we're good
        return True

    def cleanup(self, force: bool=False):
        """
        Delete contents of temporary directory

        If the temp_directory is outside the system temporary directory or

        Args:
            force (bool): If ``True``, remove git directory no matter where it is
        """
        if not force and not (
                str(self.temp_directory).startswith(tempfile.gettempdir()) or
                str(self.temp_directory).startswith(str(Config().git_dir))
        ):
            warnings.warn('Temp directory is outside of the system temp dir or git directory set by environmental variables, not deleting in case this has been changed by mistake')
            self._temp_directory = None
            return

        shutil.rmtree(str(self.temp_directory))
        self._temp_directory = None

    def clone(self, force:bool=False):
        """
        Clone the repository into the temporary directory

        Args:
            force (bool): If files are present in the temp directory,  delete them

        Raises:
            :class:`.GitError` - if the repository can't be cloned
        """
        if any(self.temp_directory.iterdir()):
            if force:
                self.cleanup()
            else:
                if not self.check():
                    warnings.warn('Destination directory is not empty and does not pass checks for correctness! cleaning up')
                    self.cleanup()
                else:
                    # already have it, just ensure commit and return
                    self.commit = self.commit
                    return
        elif self.temp_directory.exists():
            # exists but empty
            self.cleanup()

        res = subprocess.run(['git', 'clone', str(self.namespace.repository), str(self.temp_directory)])
        self.commit = self.commit
        if res.returncode != 0:
            raise GitError(f'Could not clone repository:\n{res.stderr}')










