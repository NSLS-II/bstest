import epics
import bstest._utils as UTILS

class IOCInfo:

    def __init__(self, prefix):

        self.prefix = prefix
        self.is_ad = False
        self.is_motion = False
        self.ad_core_version = None
        self.motor_core_version = None
        self.base_version = None
        self.driver_version = None
        self.ioc_type = None


    def collect_info(self):
        self.ad_core_version = epics.caget(f'{self.prefix}cam1:ADCoreVersion_RBV')
        if self.ad_core_version is not None:
            self.driver_version = epics.caget(f'{self.prefix}cam1:DriverVersion_RBV')
            self.is_ad = True

        #self.motor_core_version = epics.caget(f'{self.prefix}')
        self.base_version = epics.caget(f'{self.prefix}:EPICS_VERSION')
        self.get_ioc_type()


    def get_ioc_type(self):
        self.ioc_type = 'ADSimDetector'
