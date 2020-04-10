#!/usr/bin/env python3

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

from bluesky.tests.conftest import RE
