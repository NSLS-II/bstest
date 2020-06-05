
import pytest
from ophyd import Device as OphydDevice
from ophyd import Component as Cpt

from bstest.conftest import SimKlass

import bluesky.plans as bp
import epics

"""
@pytest.fixture(scope='function')
def AD(request):
    pre = 'XF17BM-BI{Sim-Cam:1}'
    ad_obj = SimKlass(pre, name='det')
    return ad_obj, pre



def test_simple_scan(RE, AD):
    ad_obj, _ = AD
    assert isinstance(ad_obj, OphydDevice)
    assert hasattr(ad_obj, 'cam')
    assert hasattr(ad_obj, 'ac_period')
    assert isinstance(type(ad_obj).ac_period, Cpt)
    try:
        RE(bp.count([ad_obj], num=5))
        assert True
    except:
        assert False

"""
