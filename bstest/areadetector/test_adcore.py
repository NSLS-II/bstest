from bstest.conftest import AD
from bstest import RE
from ophyd import Device as OphydDevice
from ophyd import Component as Cpt

import bluesky.plans as bp
import epics


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


