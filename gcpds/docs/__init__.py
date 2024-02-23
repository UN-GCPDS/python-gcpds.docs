"""
======================================================================
GitHub Integration and Workflow Management with Jupyter and ipywidgets
======================================================================

This module provides a graphical interface within Jupyter notebooks for managing GitHub
repositories, streamlining the use of ipywidgets for interactive GitHub integration.
Primary functions include repository cloning, changes committing, updates pulling, commits
pushing, and repository status checking, complemented by GitHub Actions workflow management.

Subsections
-----------
- Widgets:
    Custom ipywidgets classes enhancing text input with validation capabilities and providing
    styled interactive buttons and command layouts.
- GitHubLazy:
    The central class furnishing methods for interacting with GitHub repositories and
    orchestrating workflows.
- Interface Layout:
    A utility function to assemble and present the ipywidgets interface within a Jupyter
    notebook environment.

"""


import os
import sys
import shutil
import logging
import subprocess
from pathlib import Path
from typing import Optional, Callable

import ipywidgets as widgets
from IPython.display import display, HTML

try:
    from google.colab.userdata import get as get_secret
    WORKING_PATH: Path = Path('/').joinpath('content').resolve()
    REPOSITORY_PATH: Path = Path(
        '/').joinpath('content', 'my_repository').resolve()
except:
    from ipython_secrets import get_secret, delete_secret
    WORKING_PATH: Path = Path('.').resolve()
    REPOSITORY_PATH: Path = Path('.').joinpath('my_repository').resolve()

WORKFLOW_DIR = REPOSITORY_PATH / '.github' / 'workflows'
CURRENT_DIR = Path(__file__).parent


########################################################################
class ValidateText(widgets.Text):
    """Custom widget class extending ipywidgets.Text to provide validation.

    This widget augments the textual input with validation, altering an associated button's style to reflect validity status.

    Parameters
    ----------
    **kwargs : dict
        Additional keyword arguments to configure the widget.

    Attributes
    ----------
    validate : bool
        Indicates whether the validation mechanism is active.
    button : widgets.Button
        Button whose style changes based on the validation status.

    Methods
    -------
    _update_style(change)
        Updates the button's style dependent on the validity of the input text.

        Parameters
        ----------
        change : dict
            Information about the change, including 'type', 'name', 'old', and 'new'.

    """

    # ----------------------------------------------------------------------
    def __init__(self, **kwargs):
        """Initialize the ValidateText widget.

        Parameters
        ----------
        validate : bool, optional
            A flag to activate validation. Default is False.
        button : widgets.Button, optional
            A button widget linked to this text widget. Default is None.

        """
        super().__init__(**kwargs)
        self.validate: bool = kwargs.get('validate', False)
        self.button: widgets.Button = kwargs.get('button', None)

        if self.validate:
            self.observe(self._update_style, names='value')

    # ----------------------------------------------------------------------
    def _update_style(self, change: dict) -> None:
        """Update the style of the associated button based on the validation condition.

        Parameters
        ----------
        change : dict
            A dictionary containing the details of the change event. This includes keys
            such as 'type', 'name', 'old', and 'new' corresponding to the change event properties.

        Returns
        -------
        None

        """
        new_value = change['new']
        cond = bool(new_value) if self.validate is True else new_value.startswith(
            self.validate)

        self.button.button_style = 'success' if cond else 'danger'
        self.button.disabled = not cond


########################################################################
class CustomButton(widgets.Button):
    """A custom button widget with a predefined layout and optional callback functionality.

    Parameters
    ----------
    callback : Optional[Callable], optional
        The function to be called when the button is clicked. Defaults to None.

    Attributes
    ----------
    layout : widgets.Layout
        The layout configuration for the button widget.

    Methods
    -------
    __init__(callback: Optional[Callable] = None, **kwargs)
        Constructs a CustomButton instance.

    Notes
    -----
    The CustomButton can be linked to a specific functionality through the callback, which triggers upon a button click event.

    """

    # ----------------------------------------------------------------------
    def __init__(self, callback: Optional[Callable] = None, **kwargs):
        """Construct a CustomButton instance.

        Parameters
        ----------
        callback : Optional[Callable], optional
            The function to be invoked when the button is clicked.
            If not provided, no function will be called. Default is None.
        **kwargs : dict, optional
            Additional keyword arguments to pass to the base Button class.

        """
        super().__init__(**kwargs)
        self.layout = widgets.Layout(
            height='37px', width=kwargs.get('width', 'none'))

        if callback:
            self.on_click(callback)


########################################################################
class CommandLayout:
    """A layout class that combines a text widget with a custom button for command inputs.

    Parameters
    ----------
    description : str
        The description for the text widget.
    button : str
        The label for the button.
    callback : Optional[Callable], optional
        The function to call when the button is clicked, by default None.
    placeholder : str, optional
        Placeholder text for the text widget, by default ''.
    validate : bool, optional
        Whether to enable validation on the text widget, by default False.
    tooltip : str, optional
        Tooltip text for the text widget, by default ''.

    Attributes
    ----------
    button : CustomButton
        The custom button associated with the command layout.
    validate_text : ValidateText
        The ValidateText widget used for command input.

    Methods
    -------
    layout() -> widgets.AppLayout
        Returns the widget layout for the command layout, combining the text widget and the button.
    text() -> str
        Gets the current text value of the text widget.
    text(value: str)
        Sets the text value of the text widget.

    """

    # ----------------------------------------------------------------------
    def __init__(self, description: str, button: str, callback: Optional[Callable] = None,
                 placeholder: str = '', validate: bool = False, tooltip: str = ''):
        """Construct a `CommandLayout` instance with integrated text validation and command execution.

        Parameters
        ----------
        description : str
            A descriptive label for the text input field.
        button : str
            The text to display on the action button.
        callback : Optional[Callable], optional
            The callback function to invoke when the action button is clicked. Default is None.
        placeholder : str, optional
            The placeholder text for the text input when it is empty. Default is an empty string.
        validate : bool, optional
            A flag to indicate if validation should be applied to the text input. Default is False.
        tooltip : str, optional
            A short text to help the user understand what the text input and button are for. Default is an empty string.

        Returns
        -------
        None
        """
        self.button = CustomButton(
            description=button, button_style='danger', disabled=True, tooltip=tooltip)
        self.validate_text = ValidateText(
            placeholder=placeholder,
            description=description,
            disabled=False,
            validate=validate,
            button=self.button,
            layout=widgets.Layout(width='100%', padding='5px')
        )

        if callback:
            self.button.on_click(callback)

    # ----------------------------------------------------------------------
    @property
    def layout(self) -> widgets.AppLayout:
        """Construct the widget layout for the command layout.

        Returns
        -------
        widgets.AppLayout
            The layout combining the text widget and the button.
        """

        return widgets.AppLayout(center=self.validate_text, right_sidebar=self.button)

    # ----------------------------------------------------------------------
    @property
    def text(self) -> str:
        """Get the current text value of the text widget.

        Returns
        -------
        str
            The current text value of the text widget.
        """
        return self.validate_text.value

    # ----------------------------------------------------------------------
    @text.setter
    def text(self, value: str) -> None:
        """Set the text value of the text widget.

        Parameters
        ----------
        value : str
            The text value to set.
        """
        self.validate_text.value = value


########################################################################
class GitHubLazy:
    """Handles GitHub operations within a Jupyter notebook using ipywidgets.

    This class allows for common GitHub operations such as cloning a repository,
    committing changes, pulling updates, pushing commits, and checking statuses—all
    through an interactive IPython widget interface.

    Attributes
    ----------
    GITHUB_PAT : Optional[str]
        A GitHub Personal Access Token for authentication, retrieved from secrets.
    GITHUB_NAME : Optional[str]
        The GitHub username associated with the token, retrieved from secrets.
    GITHUB_EMAIL : Optional[str]
        The email address associated with the GitHub account, retrieved from secrets.
    logger : widgets.Label
        A widget label for logging output within the Jupyter notebook.

    Methods
    -------
    __init__()
        Initializes the GitHubLazy object with all necessary widgets and configuration.

    Raises
    ------
    Exception
        If a required secret (like GITHUB_PAT) is not set or if an operation fails.

    Notes
    -----
    It is necessary to set the GitHub personal access token (GITHUB_PAT), username (GITHUB_NAME),
    and email (GITHUB_EMAIL) as secrets prior to using this class for GitHub operations.

    Examples
    --------
    >>> github = GitHubLazy()
    >>> github.clone_repository('https://github.com/user/repo.git')
    Cloning into 'repo'...
    >>> github.commit_changes('Initial commit')
    [main (root-commit) 1a2b3c4] Initial commit
    """

    GITHUB_PAT: Optional[str] = get_secret('GITHUB_PAT')
    GITHUB_NAME: Optional[str] = get_secret('GITHUB_NAME')
    GITHUB_EMAIL: Optional[str] = get_secret('GITHUB_EMAIL')

    logger: widgets.Label = widgets.Label(
        '', layout=widgets.Layout(font_family='monospace', font_size='20px'))
    logger.add_class('lab-logger')

    # ----------------------------------------------------------------------
    def __init__(self):
        """Initialize the GitHubLazy object with all necessary widgets and configuration.

        Raises
        ------
        Exception
            If a required secret (like GITHUB_PAT) is not set or if an operation fails.

        """

        self.github_title = widgets.Label(
            "GitHub Integration for Jupyter: Simplified Management")
        self.github_title.add_class('title-size')

        self.github_header = widgets.Label("This tool is an integrated system for managing GitHub repositories within a Jupyter Notebook environment. It offers a user-friendly graphical interface that simplifies common Git operations, making them more accessible to users of all skill levels.",
                                           # layout=widgets.Layout(height='100px'),
                                           )
        self.github_header.add_class('text-wrap')

        self.clone_layout = CommandLayout('Repository', 'Clone', callback=self.clone,
                                          placeholder='https://github.com/<organization|user>/<repository>.git',
                                          validate='https://github.com/',
                                          tooltip="Creates a local copy of a remote repository. This command is used to download existing source code from a remote repository to a local machine.",
                                          )
        self.commit_layout = CommandLayout('Message', 'Commit', callback=self.commit,
                                           placeholder='Update',
                                           validate=True,
                                           tooltip="Records changes made to files in a local repository. A commit saves a snapshot of the project's currently staged changes.",
                                           )

        self.status_button = CustomButton(description='Status', button_style='info', callback=self.status,
                                          tooltip="Displays the state of the working directory and the staging area. It shows which changes have been staged, which haven't, and which files aren't being tracked by Git.")
        self.pull_button = CustomButton(description='Pull', button_style='info', callback=self.pull,
                                        tooltip="Fetches changes from a remote repository and merges them into the local branch. This is used to update the local code with changes from others.")
        self.push_button = CustomButton(description='Push', button_style='warning', callback=self.push,
                                        tooltip="Updates the remote repository with any commits made locally to a branch. It's a way to share your changes with others.")

        self.github_button_layout = widgets.HBox([self.status_button, self.pull_button, self.push_button],
                                                 layout=widgets.Layout(justify_content='flex-start', width='100%'))

        yml_files = []
        for yml_file in CURRENT_DIR.glob('*.yml'):
            checkbox = widgets.Checkbox(value=(WORKFLOW_DIR / yml_file.name).exists(),
                                        description=yml_file.name,
                                        disabled=False,
                                        indent=True,
                                        layout=widgets.Layout(width='90%'),
                                        )
            checkbox.observe(lambda evt, yml_file=yml_file: self.copy_workflow(
                yml_file), names='value')
            yml_files.append(checkbox)

        if yml_files:
            self.webhooks_title = widgets.Label(
                "Automated Workflow Creation for GitHub Repositories")
            self.webhooks_title.add_class('title-size')
            self.right_button_layout = widgets.VBox(
                yml_files, layout=widgets.Layout(justify_content='flex-start', width='100%'))

        self.run_command(
            f'git config --global user.name "{self.GITHUB_NAME}"', silent=True)
        self.run_command(
            f'git config --global user.email "{self.GITHUB_EMAIL}"', silent=True)

    # ----------------------------------------------------------------------
    def run_command(self, command: str, path: str = '.', silent: bool = True) -> None:
        """Execute a given shell command in the specified directory path.

        Parameters
        ----------
        command : str
            The shell command to execute.
        path : str, optional
            The directory path where the command is to be executed. Default is the current directory.
        silent : bool, optional
            If True, suppresses the logging output. Default is True.

        """

        original_dir = os.getcwd()
        os.chdir(path)

        if not silent:
            logging.warning(f'Original directory: {original_dir}')
            logging.warning(f'Moving to {path}')
            logging.warning(f'Running command: {command}')

        result = subprocess.run(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        stdout, stderr = result.stdout, result.stderr
        self.logger.value = f'{stdout}\n{stderr}'

        os.chdir(original_dir)

        if not silent:
            logging.warning(f'Back again to {original_dir}')

    # ----------------------------------------------------------------------
    def clone(self, evt: Optional[widgets.Button] = None) -> None:
        """Clone a GitHub repository.

        This method is designed to clone a GitHub repository using the repository URL provided through
        the clone_layout text widget interface.

        Parameters
        ----------
        evt : Optional[widgets.Button], optional
            The button event that triggers the cloning process. If no event is provided, the method
            can be called programmatically without any event context. Default is None.

        Raises
        ------
        subprocess.CalledProcessError
            If the cloning process encounters an error.

        Examples
        --------
        >>> github = GitHubLazy()
        >>> github.clone(None)
        # Assume the URL is already provided through the interface; this will start the cloning process.

        """

        repository_url = self.clone_layout.text.removeprefix('https://')
        self.run_command(
            f"git clone https://{self.GITHUB_PAT}@{repository_url} my_repository", path=WORKING_PATH)
        self.run_command('git config pull.rebase true', silent=True)
        self.run_command(
            'git config --global credential.helper cache', silent=True)
        sys.path.append(REPOSITORY_PATH)

    # ----------------------------------------------------------------------
    def commit(self, evt: Optional[widgets.Button] = None) -> None:
        """Commit changes to the local repository with a message.

        The commit message is provided through the commit_layout's text widget.
        This allows users to specify what changes they're committing.

        Parameters
        ----------
        evt : Optional[widgets.Button], optional
            The event associated with the commit button that, when triggered,
            calls this method. If `None`, the method can be called without
            an event, allowing for programmatic commits (default is None).

        Raises
        ------
        subprocess.CalledProcessError
            If the commit process fails due to underlying issues with the Git command.

        Examples
        --------
        >>> github_lazy = GitHubLazy()
        >>> github_lazy.commit(None)  # This assumes that the commit message is pre-set.

        """

        self.run_command("git add .", path=REPOSITORY_PATH)
        self.run_command("git add -f .github", path=REPOSITORY_PATH)
        self.run_command(
            f"git commit -m '{self.commit_layout.text.strip()}'", path=REPOSITORY_PATH)
        self.commit_layout.text = ''

    # ----------------------------------------------------------------------
    def pull(self, evt: Optional[widgets.Button] = None) -> None:
        """Fetch the most recent changes from the remote repository and merge them with the local branch.

        This will update the local copy of the repository with any changes that have been made remotely.

        Parameters
        ----------
        evt : Optional[widgets.Button], optional
            The button event that triggers the pull operation. If the method
            is called without an associated event, it's assumed to be a manual call.
            Defaults to None.

        Examples
        --------
        >>> github_lazy = GitHubLazy()
        >>> github_lazy.pull()  # Pulls changes without a button event.
        """

        self.run_command('git config pull.rebase true', silent=True)
        self.run_command("git pull", path=REPOSITORY_PATH)

    # ----------------------------------------------------------------------
    def status(self, evt: Optional[widgets.Button] = None) -> None:
        """Checks the current status of the local Git repository.

        This method displays the current status of files in the local repository,
        indicating if files are staged, unstaged, or untracked, and if the branch is ahead,
        behind, or has diverged from the remote branch it tracks.

        Parameters
        ----------
        evt : Optional[widgets.Button], optional
            The button event that triggers the status check. If the method is
            called without an associated event, it's assumed to be a manual call.
            Default is None.

        """

        self.run_command("git status", path=REPOSITORY_PATH)

    # ----------------------------------------------------------------------
    def push(self, evt: Optional[widgets.Button] = None) -> None:
        """Pushes local commits to the remote repository.

        This method will push all committed changes in the local repository to the remote repository defined in the repository's Git configuration.

        Parameters
        ----------
        evt : Optional[widgets.Button], optional
            The button event that triggers this method. If the method is called programmatically without a button event, this argument should be None. Default is None.
        """

        self.run_command("git push", path=REPOSITORY_PATH)

    # ----------------------------------------------------------------------
    def copy_workflow(self, workflow: Path) -> None:
        """Copies the specified GitHub Actions workflow file to the repository's workflow directory.

        Parameters
        ----------
        workflow : Path
            The Path object representing the workflow file to be copied to the repository's workflow directory.

        """

        os.makedirs(WORKFLOW_DIR, exist_ok=True)
        workflow_docs_dst = REPOSITORY_PATH / '.github' / 'workflows' / workflow.name
        if workflow_docs_dst.exists():
            os.remove(workflow_docs_dst)
        else:
            shutil.copyfile(workflow, workflow_docs_dst)


# ----------------------------------------------------------------------
def delete_secrets() -> None:
    """Removes saved GitHub secrets from storage.

    This function clears out the GitHub Personal Access Token (PAT), GitHub username,
    and GitHub email address stored securely, ensuring these sensitive details are no longer retained in the system.

    Raises
    ------
    KeyError
        If a secret key does not exist in the storage when attempted to be deleted.
    """

    delete_secret('GITHUB_PAT')
    delete_secret('GITHUB_NAME')
    delete_secret('GITHUB_EMAIL')


# ----------------------------------------------------------------------
def __lab__() -> widgets.GridspecLayout:
    """Creates and displays a GitHub management interface using ipywidgets.

    This function initializes the GitHubLazy class and arranges its components into a GridspecLayout for display.

    Returns
    -------
    widgets.GridspecLayout
        A grid layout containing the GitHubLazy interface components.

    """
    lab = GitHubLazy()

    # Define the layout components
    layouts = [
        lab.github_title,
        lab.github_header,
    ]

    if not REPOSITORY_PATH.exists():
        layouts.append(lab.clone_layout.layout)
    else:
        layouts.extend([
            lab.commit_layout.layout,
            lab.github_button_layout,
        ])

    if hasattr(lab, 'webhooks_title'):
        layouts.append(lab.webhooks_title)

    if hasattr(lab, 'right_button_layout'):
        layouts.append(lab.right_button_layout)

    layouts.append(lab.logger)

    # Apply CSS styles to the logger
    display(HTML(
        '<style> .lab-logger { font-family: monospace; text-wrap: pretty; height: auto !important } </style>'))
    display(HTML(
        '<style> .text-wrap { text-wrap: pretty; line-height: 130%; height: auto !important; } </style>'))
    display(
        HTML('<style> .title-size { font-size: 150%; margin-top: 20px; } </style>'))

    grid = widgets.VBox(layouts, layout=widgets.Layout(
        justify_content='flex-start', width='100%'))
    return grid
