from bstest.conftest import AD
from bstest import RE
from ophyd import Device as OphydDevice
from ophyd import Component as Cpt

import bluesky.plans as bp

def test_simple_scan(RE, AD):
    assert isinstance(AD, OphydDevice)
    assert hasattr(AD, 'cam')
    assert hasattr(AD, 'ac_period')
    assert isinstance(type(AD).ac_period, Cpt)
    try:
        RE(bp.count([AD], num=5))
        assert True
    except:
        assert False
