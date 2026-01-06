# -*- coding: UTF-8 -*-
"""
Steam Information
=================
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
The steam information parser.

This package is implemented solely using the network access to the Steam public
APIs.

Note that the usages of such APIs are undocumented. The performance of this package
may not be ensured. If there are any issues with the results, please submit them to
the GitHub issue tracker of this project.
"""

from pkgutil import extend_path

from . import utils
from . import data
from . import query

from .data import AppQuerySimple, AppInfo
from .query import query_app_by_name_simple, get_app_details


__all__ = (
    "utils",
    "data",
    "query",
    "AppQuerySimple",
    "AppInfo",
    "query_app_by_name_simple",
    "get_app_details",
)

# Set this local module as the prefered one
__path__ = extend_path(__path__, __name__)

# Delete private sub-modules and objects
del extend_path
