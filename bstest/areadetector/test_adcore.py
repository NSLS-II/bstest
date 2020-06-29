from ophyd import Device as OphydDevice
from ophyd import Component as Cpt
import bluesky.plans as bp

import epics

import bstest
import bstest._utils
import pytest


if bstest.is_external_ioc() and not bstest._utils.get_ioc_type(bstest.EXTERNAL_PREFIX).is_ad:
    pytest.skip('Skipping areaDetector specific tests', allow_module_level=True)


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


def test_stats_stress_test(RE, AD):
    ad_obj, prefix = AD
    stats_plugin_counter = 1
    while epics.caput(f'{prefix}Stats{stats_plugin_counter}:EnableCallbacks', 1, timeout=1) is not None:
        if stats_plugin_counter > 1:
            pass

    RE(bp.count([ad_obj], num=100))
    for i in range(1, stats_plugin_counter):
        assert epics.caget(f'{prefix}Stats{i}:DroppedArrays_RBV') == 0
