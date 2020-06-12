
import bstest
import epics
import sys
import random


def gen_n_digit_number(n):
    """Generates a random n digit number

    Parameters
    ----------
    n : int
        Number of digits output should have

    Returns
    -------
    int
        A pseudo random n-digit number
    """

    return random.randing(10**(n-1), (10**n) - 1)


def get_environment():
    """Helper function that identifies current environment information

    Returns
    -------
    str
        String representing python environment and os environment
    """
    
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


def is_ioc_ready(prefix, timeout = 1):
    """Checks to ensure that IOC is active

    Attempts to caget the EPICS_VERSION PV that should be available 
    for all IOCs.

    Parameters
    ----------
    prefix : str
        Prefix of epics IOC to test
    timeout : int
        Number of seconds to wait for responce from IOC. Default: 1
    
    Returns
    -------
    bool
        True if return from caget is not None, False otherwise
    """

    return epics.caget(f'{prefix}:EPICS_VERSION', timeout=timeout) is not None 


def wait_for_ioc_readiness(prefix, max_wait_time=10):
    """Function that waits for the IOC process to be visible.

    Parameters
    ----------
    prefix : str
        Prefix of epics IOC to wait for
    max_wait_time : int
        Maximum number of seconds to wait for IOC to be ready. Default: 10

    Returns
    -------
    bool
        True if IOC is ready before max_wait_time is reached, false otherwise
    """

    wait_time = 0
    while wait_time <= max_wait_time:
        if is_ioc_ready(prefix):
            return True
        wait_time += 1
    return False


def get_ioc_type(prefix):
    """Function that attempts to guess the type of an IOC

    Parameters
    ----------
    prefix : str
        The prefix of the target IOC

    Returns
    -------
    str
        The type of the IOC
    """

    if wait_for_ioc_readiness(prefix):
        pass   
    else:
        return None



