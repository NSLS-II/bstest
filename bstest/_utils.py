
import bstest
import epics


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



