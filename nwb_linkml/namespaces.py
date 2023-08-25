"""
Define and manage NWB namespaces in external repositories
"""
import warnings
from pathlib import Path
import tempfile
import subprocess
import shutil

from pydantic import BaseModel, HttpUrl, FilePath, DirectoryPath, Field

class NamespaceRepo(BaseModel):
    """
    Definition of one NWB namespaces file to import from a git repository
    """
    name: str = Field(description="Short name used to refer to this namespace (usually equivalent to the name field within a namespaces NWB list)")
    repository: HttpUrl | DirectoryPath = Field(description="URL or local absolute path to the root repository")
    path: Path = Field(description="Relative path from the repository root to the namespace file")

    def provide_from_git(self, commit:str|None=None) -> Path:
        git = GitRepo(self, commit)
        git.clone()
        return git.namespace_file

# Constant namespaces
NWB_CORE_REPO = NamespaceRepo(
    name="core",
    repository="https://github.com/NeurodataWithoutBorders/nwb-schema",
    path=Path("core/nwb.namespace.yaml")
)

HDMF_COMMON_REPO = NamespaceRepo(
    name="hdmf-common",
    repository="https://github.com/hdmf-dev/hdmf-common-schema",
    path=Path("common/namespace.yaml")
)

DEFAULT_REPOS = {
    repo.name: repo for repo in [NWB_CORE_REPO, HDMF_COMMON_REPO]
}


class GitError(OSError):
    pass

class GitRepo:
    """
    Manage a temporary git repository that provides the NWB yaml files
    """
    def __init__(self, namespace:NamespaceRepo, commit:str|None=None):
        self._temp_directory = None
        self.namespace = namespace
        self.commit = commit

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
            self._temp_directory = Path(tempfile.gettempdir()) / f'nwb_linkml__{self.namespace.name}'
            if self._temp_directory.exists():
                warnings.warn(f'Temporary directory already exists! {self._temp_directory}')
            else:
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
                warnings.warn('At wrong commit')
                return False

        except GitError:
            return False

        # Check that the remote matches
        if self.remote.strip('.git') != self.namespace.repository:
            warnings.warn('Repository exists, but has the wrong remote URL')
            return False

        # otherwise we're good
        return True

    def cleanup(self):
        """
        Delete contents of temporary directory
        """
        if not str(self.temp_directory).startswith(tempfile.gettempdir()):
            warnings.warn('Temp directory is outside of the system temp dir, not deleting in case this has been changed by mistake')
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
                    # already have it
                    return
        elif self.temp_directory.exists():
            # exists but empty
            self.cleanup()

        res = subprocess.run(['git', 'clone', str(self.namespace.repository), str(self.temp_directory)])
        if res.returncode != 0:
            raise GitError(f'Could not clone repository:\n{res.stderr}')










