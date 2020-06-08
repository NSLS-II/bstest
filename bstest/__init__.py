from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

from bluesky.tests.conftest import RE

__copyright__ = 'Copyright (c) Brookhaven National Laboratory - 2020'


import sys

def get_environment():
    if sys.platform == 'win32':
        OS_class = 'windows-x64'
    elif sys.platform == 'darwin':
        OS_class = 'Mac OS'
    else:
        try:
            import distro
            v = distro.linux_distribution(full_distribution_name=False)
            OS_class = f'{v[0]}_{v[1]}'
        except:
            OS_class = 'linux'

    return f'Python Version: {sys.version.split()[0]}, OS Class: {OS_class}'
