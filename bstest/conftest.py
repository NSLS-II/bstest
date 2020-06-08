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
import random

import epics

from nslsii.ad33 import SingleTriggerV33
from ophyd.areadetector.cam import AreaDetectorCam
from ophyd.areadetector.detectors import DetectorBase
from ophyd import Component as Cpt,  EpicsSignal
from bluesky.tests.conftest import RE

import pytest

import bstest._utils as UTILS

# make the logs noisy
logger = logging.getLogger('bstest')
logger.setLevel('DEBUG')


@pytest.fixture(scope='function')
def prefix():
    """Generate a random prefix for example IOCs
    """

    return f"BSTEST-DEMOIOC[{random.randint(100, 999)}]"


@pytest.fixture(scope='function')
def container_name():

    return f'container_{random.randint(100000, 999999)}'


def spawn_example_ioc(pre, request, container_type, container_name, 
                        container_wd, env_vars = {}, stdin=None, stdout=None, stderr=None):

    """Spawns a default an example Dockerized-IOC as a subprocess
    """
    
    full_container_name = f'{container_type}_{container_name}'
    p = subprocess.Popen(['docker', 'run', '-e', f'P="{pre}"', 
                            '-w', container_wd, 
                            '-itd', '--name', full_container_name, 
                            '--rm', f'epics-ioc/{container_type}'],
                             stdout=stdout, stderr=stderr, stdin=stdin)

    def stop_ioc():
        _ = subprocess.call(['docker', 'kill', full_container_name])
    
    
    if request is not None:
        request.addfinalizer(stop_ioc)

    if UTILS.wait_for_ioc_readiness(pre):
        logger.debug(f'Spawned {full_container_name} example IOC successfully')
        return p
    else:
        logger.debug('Failed to establish connection to IOC in given timeout')
        return None 


class MyDetector(SingleTriggerV33, AreaDetectorCam):
    pass


class SimKlass(SingleTriggerV33, DetectorBase):
    cam = Cpt(MyDetector, "cam1:")

    ac_period = Cpt(EpicsSignal, "cam1:AcquirePeriod")


@pytest.fixture(scope='function')
def AD(request, prefix, container_name):
    _ = spawn_example_ioc(prefix, request, 'simdetector', 
                            container_name, '/epics/iocs/cam-sim1')

    ad_obj = SimKlass(prefix, name='det')
    return ad_obj, prefix
