from bstest.conftest import AD
from bstest import RE
from ophyd import Device as OphydDevice
from ophyd import Component as Cpt


def test_simple_scan(RE, AD):
    assert isinstance(AD, OphydDevice)
    assert hasattr(AD, 'cam')
    assert hasattr(AD, 'ac_period')
    assert isinstance(AD.ac_period, Cpt)
    try:
        RE(count[det], num=5)
        assert True
    except:
        assert False