# -*- coding: UTF-8 -*-
"""
Utilities
=========
@ Steam Editor Tools

Author
------
Yuchen Jin (cainmagi)
cainmagi@gmail.com

License
-------
MIT License

Description
-----------
The utilities of this package. The utilities in this module are designed for
general use.
"""

import os
import contextlib
import tempfile
import shutil
import types

from typing import TypeVar


_BaseException = TypeVar("_BaseException", bound=BaseException)
__all__ = ("NamedTempFolder",)


class NamedTempFolder(contextlib.AbstractContextManager):
    """Named temporary folder.

    Similar to `tempfile.NamedTemporaryFile`. This context maintain a temporary
    folder that can be accessed by the path. When exiting from the context, the
    temporary folder will be automatically deleted.
    """

    __slots__ = ("folder_path", "__current_path")

    def __init__(self, folder_path: "str | os.PathLike[str] | None" = None) -> None:
        """Initialization.

        Arguments
        ---------
        folder_path: `str | PathLike[str] | None`
            The path to the temporary folder. If not specified, will use
            `tempfile.mkdtemp()` to create the folder.

            Note that if the specified folder path exists, will automatically add
            postfix to the given path until a new folder can be maintained.
        """
        if folder_path:
            folder_path = str(folder_path)
            base_path = folder_path
            num = 0
            while os.path.exists(folder_path):
                folder_path = os.path.join(base_path, "temp{0:03d}".format(num))
                num = num + 1
        else:
            folder_path = None
        self.folder_path: str | None = folder_path
        self.__current_path: str | None = None

    @property
    def current_path(self) -> str | None:
        """Property: Get the current temporary folder path. If not in the context,
        this value will be `None`."""
        return self.__current_path

    def close(self) -> None:
        """Close the temporary folder. Will delete the folder and reset the status
        to the status that is not in the context.

        This method will be automatically called when exiting from this context.
        """
        if isinstance(self.__current_path, str) and self.__current_path:
            shutil.rmtree(self.__current_path, ignore_errors=True)
        self.__current_path = None

    def __enter__(self) -> str:
        """Enter the context."""
        self.close()
        if self.folder_path is None:
            current_path = tempfile.mkdtemp(suffix=None, prefix=None, dir=None)
        else:
            current_path = self.folder_path
            os.makedirs(current_path, exist_ok=True)
        self.__current_path = current_path
        return current_path

    def __exit__(
        self,
        exc_type: type[_BaseException] | None,
        exc_value: _BaseException | None,
        traceback: types.TracebackType | None,
    ) -> bool | None:
        """Raise any exception triggered within the runtime context."""
        self.close()
        return None
