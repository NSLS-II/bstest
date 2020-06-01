import pytest
import ophyd
import logging
import os
import subprocess
import sys
import threading
import time
import uuid
import signal
import epics

from caproto.tests import conftest as caproto_utils

# make the logs noisy
logger = logging.getLogger('bstest')
logger.setLevel('DEBUG')


def assert_array_equal(arr1, arr2):
    assert len(arr1) == len(arr2)
    for i, j in zip(arr1, arr2):
        assert i == j


def assert_array_almost_equal(arr1, arr2):
    assert len(arr1) == len(arr2)
    for i, j in zip(arr1, arr2):
        assert abs(i - j) < 1e-6


@pytest.fixture(scope='function')
def prefix():
    """Generate a random prefix for example IOCs
    """

    # TODO: Remove this hardcoded prefix
    return 'DEVSIM1:'


def spawn_example_ioc(pre, ioc_config_path, request, stdin=None, stdout=None, stderr=None):
    """Spawns a default an example SimDetector IOC as a subprocess
    """

    os.environ['P'] = pre
    current_dir = os.getcwd()
    os.chdir(ioc_config_path)
    print(ioc_config_path)
    print(os.listdir(ioc_config_path))
    p = subprocess.Popen(['./st.cmd'],
                         stdout=stdout, stderr=stderr, stdin=stdin,
                         env=os.environ)
    os.chdir(current_dir)

    def stop_ioc():
        if p.poll() is None:
            if sys.platform != 'win32':
                logger.debug('Sending Ctrl-C to the example IOC')
                p.send_signal(signal.SIGINT)
                logger.debug('Waiting on process...')

            try:
                p.wait(timeout=1)
            except subprocess.TimeoutExpired:
                logger.debug('IOC did not exit in a timely fashion')
                p.terminate()
                logger.debug('IOC terminated')
            else:
                logger.debug('IOC has exited')
        else:
            logger.debug('Example IOC has already exited')

    if request is not None:
        request.addfinalizer(stop_ioc)

    time.sleep(15)

    return p


from nslsii.ad33 import SingleTriggerV33
#from ophyd import SingleTrigger
from ophyd.areadetector.cam import AreaDetectorCam
from ophyd.areadetector.detectors import DetectorBase
from ophyd import Component as Cpt,  EpicsSignal
from contextlib import contextmanager

import pytest

class MyDetector(SingleTriggerV33, AreaDetectorCam):
    pass


class SimKlass(SingleTriggerV33, DetectorBase):
    cam = Cpt(MyDetector, "cam1:")

    ac_period = Cpt(EpicsSignal, "cam1:AcquirePeriod")


@pytest.fixture(scope='function')
def pv_to_check(prefix):
    return f'{prefix}cam1:AcquireTime_RBV'


@contextmanager
def softioc(prefix, ioc_path, additional_args=None,
            macros=None, env=None):
    '''[context manager] Start a soft IOC on-demand
    Parameters
    ----------
    prefix : str
        The prefix for the test IOC
    ioc_path : os.pathlike
        the path to the IOC st.cmd script
    additional_args : list
        List of additional args to pass to softIoc
    macros : dict
        Dictionary of key to value
    env : dict
        Environment variables to pass
    Yields
    ------
    proc : subprocess.Process
    '''

    if additional_args is None:
        additional_args = []

    if macros is None:
        macros = dict(P=prefix)

    proc_env = os.environ.copy()
    if env is not None:
        proc_env.update(**env)

    logger.debug('soft ioc environment is:')
    for key, val in sorted(proc_env.items()):
        if not key.startswith('_'):
            logger.debug('%s = %r', key, val)

    # if 'EPICS_' not in proc_env:

    macros = ','.join('{}={}'.format(k, v) for k, v in macros.items())

    popen_args = [executable,
                  '-m', macros]

    if sys.platform == 'win32':
        si = subprocess.STARTUPINFO()
        si.dwFlags = (subprocess.STARTF_USESTDHANDLES |
                      subprocess.CREATE_NEW_PROCESS_GROUP)
        os_kwargs = dict(startupinfo=si)
        executable = 'st.cmd'
    else:
        os_kwargs = {}
        executable = './st.cmd'

    cwd = os.getcwd()
    os.chdir(ioc_path)

    proc = subprocess.Popen(popen_args + additional_args, env=proc_env,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            **os_kwargs)

    os.chdir(cwd)

    try:
        yield proc
    finally:
        proc.kill()
        proc.wait()



@pytest.fixture(scope='function')
def AD(request, prefix):
    fp = open('test.txt', 'w')
    _           = spawn_example_ioc(prefix, '/home/jwlodek/Workspace/iocs/cam-sim1', request, stdout=fp, stderr=fp)
    print(epics.caget(f'{prefix}AcquirePeriod_RBV'))
    ad_obj      = SimKlass(prefix, name='det')
    return ad_obj
