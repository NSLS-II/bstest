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
    return "XF17BM-BI{Sim-Cam:1}"


def spawn_example_ioc(pre, request, stdin=None, stdout=None, stderr=None):
    """Spawns a default an example SimDetector IOC as a subprocess
    """

    p = subprocess.Popen(['docker', 'run', '-w', '/epics/iocs/cam-sim1', 
                            '-itd', '--name', 'fixture_test', '--rm', 'ioc/simdetector'],
                         stdout=stdout, stderr=stderr, stdin=stdin)
                         #env=os.environ)

    def stop_ioc():
        _ = subprocess.call(['docker', 'kill', 'fixture_test'])
    
    
    if request is not None:
        request.addfinalizer(stop_ioc)

#    time.sleep(10)
    ioc_active = False
    loop_counter = 0
    while not ioc_active and loop_counter <= 6:
        if epics.caget(f'{pre}cam1:ADCoreVersion_RBV', timeout=1) is not None:
            ioc_active=True
        loop_counter += 1

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
def AD(request, prefix):
    fp = open('test.txt', 'w')
    _           = spawn_example_ioc(prefix, request, stdout=fp, stderr=fp)
    ad_obj      = SimKlass(prefix, name='det')
    return ad_obj, prefix
