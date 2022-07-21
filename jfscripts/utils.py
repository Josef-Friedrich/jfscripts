from __future__ import annotations

import os
import shutil
import subprocess
from argparse import ArgumentParser
from typing import Callable, List, Tuple

from termcolor import colored


class Run:

    PIPE = subprocess.PIPE

    def __init__(self, *args, **kwargs):
        self.setup(*args, **kwargs)

    def setup(self, verbose=False, colorize=False):
        self.verbose = verbose
        self.colorize = colorize

    def _print_cmd(self, cmd):
        if self.colorize:
            output = []
            for arg in cmd:
                if arg.startswith("--"):
                    output.append(colored(arg, color="yellow"))
                elif arg.startswith("-"):
                    output.append(colored(arg, color="blue"))
                elif os.path.exists(arg):
                    output.append(colored(arg, color="white", on_color="on_cyan"))
                else:
                    output.append(arg)
            print(" ".join(output))
        else:
            print(" ".join(cmd))

    def run(self, *args, **kwargs):
        """
        :return: A `CompletedProcess` object.
        :rtype: subprocess.CompletedProcess
        """
        if self.verbose:
            self._print_cmd(args[0])
        return subprocess.run(*args, **kwargs)

    def check_output(self, *args, **kwargs):
        if self.verbose:
            self._print_cmd(args[0])
        return subprocess.check_output(*args, **kwargs)


def check_dependencies(
    *executables: Tuple[str, str] | str, raise_error: bool = True
) -> bool:
    """Check if the given executables are existing in $PATH.

    :param executables: A tuple of executables to check for their
      existence in $PATH. Each element of the tuple can be either a string
      (e. g. `pdfimages`) or a itself a tuple `('pdfimages', 'poppler')`.
      The first entry of this tuple is the name of the executable the second
      entry is a description text which is displayed in the raised exception.

    :param raise_error: Raise an error if an executable doesn’t exist.

    :return: True if all executables exist. False if one or
      more executables not exist.
    """
    errors: List[str] = []
    for executable in executables:
        if isinstance(executable, tuple):
            if not shutil.which(executable[0]):
                errors.append("{} ({})".format(executable[0], executable[1]))
        else:
            if not shutil.which(executable):
                errors.append(executable)

    if errors:
        if raise_error:
            raise SystemError("Some commands are not installed: " + ", ".join(errors))
        else:
            return False
    else:
        return True


class FilePath:
    absolute: bool
    """Boolean value indicating whether the path is an absolute or an
    relative path."""

    filename: str
    """The filename is the combination of the basename and the
    extension, e. g. `file.ext`."""

    extension: str
    """The extension of the file, e. g. `ext`."""

    basename: str
    """The basename of the file, e. g. `file`."""

    base: str
    """The path without an extension, e. g. `/home/document/file`."""

    def __init__(self, path: str, absolute: bool = False):
        self.absolute = absolute
        if self.absolute:
            self.path = os.path.abspath(path)
        else:
            self.path = os.path.relpath(path)
        self.filename = os.path.basename(path)
        self.extension = os.path.splitext(self.path)[1][1:]
        self.basename = self.filename[: -len(self.extension) - 1]
        self.base = self.path[: -len(self.extension) - 1]

    def __str__(self):
        return self.path

    def __eq__(self, other: object) -> bool:
        return self.path == other.path

    def _export(self, path: str) -> FilePath:
        return FilePath(path, self.absolute)

    def new(
        self, extension: str | None = None, append: str = "", del_substring: str = ""
    ) -> FilePath:
        """
        :param extension: The extension of the new file path.
        :param append: String to append on the basename. This string
          is located before the extension.
        :param del_substring: String to delete from the new file path.

        :return: A new file path object.

        """
        if not extension:
            extension = self.extension
        new = "{}{}.{}".format(self.base, append, extension)
        if del_substring:
            new = new.replace(del_substring, "")
        return self._export(new)

    def remove(self) -> None:
        """Remove the file."""
        os.remove(self.path)


def argparser_to_readme(
    argparser: Callable[[], ArgumentParser],
    template: str = "README-template.md",
    destination: str = "README.md",
    indentation: int = 0,
    placeholder: str = "{{ argparse }}",
) -> None:
    """Add the formatted help output of a command line utility using the
    Python module `argparse` to a README file. Make sure to set the name
    of the program (`prop`) or you get strange program names.

    :param argparser: A function that returns an object.
    :param template: The path of a template text file containing the
      placeholder. Default: `README-template.md`
    :param destination: The path of the destination file. Default:
      `README.me`
    :param indentation: Indent the formatted help output by X spaces.
      Default: 0
    :param placeholder: Placeholder string that gets replaced by the
      formatted help output. Default: `{{ argparse }}`
    """
    help_string = argparser().format_help()

    if indentation > 0:
        indent_lines: List[str] = []
        lines = help_string.split("\n")
        for line in lines:
            indent_lines.append(" " * indentation + line)

        help_string = "\n".join(indent_lines)

    with open(template, "r", encoding="utf-8") as template_file:
        template_string = template_file.read()
        readme = template_string.replace(placeholder, help_string)

    readme_file = open(destination, "w")
    readme_file.write(readme)
    readme_file.close()
