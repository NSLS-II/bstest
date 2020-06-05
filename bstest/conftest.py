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
    return 'DEV1:{SimDetector-Cam:0}'


def spawn_example_ioc(ioc_config_path, request, stdin=None, stdout=None, stderr=None):
    """Spawns a default an example SimDetector IOC as a subprocess
    """

#    os.environ['P'] = pre
    current_dir = os.getcwd()
    os.chdir(ioc_config_path)
    p = subprocess.Popen(['./st.cmd'],
                         stdout=stdout, stderr=stderr, stdin=stdin)
                         #env=os.environ)
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

    time.sleep(10)

    return p


from nslsii.ad33 import SingleTriggerV33
#from ophyd import SingleTrigger
from ophyd.areadetector.cam import AreaDetectorCam
from ophyd.areadetector.detectors import DetectorBase
from ophyd import Component as Cpt,  EpicsSignal

import pytest

class MyDetector(SingleTriggerV33, AreaDetectorCam):
    pass


class SimKlass(SingleTriggerV33, DetectorBase):
    cam = Cpt(MyDetector, "cam1:")

    ac_period = Cpt(EpicsSignal, "cam1:AcquirePeriod")


@pytest.fixture(scope='function')
def AD(request):
    fp = open('test.txt', 'w')
    _           = spawn_example_ioc('/home/jwlodek/Workspace/utils/Dockerized-IOC', request, stdout=fp, stderr=fp)
    ad_obj      = SimKlass("XF17BM-BI{Sim-Cam:1}", name='det')
    return ad_obj
