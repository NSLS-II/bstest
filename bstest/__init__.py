from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

from subprocess import Popen, PIPE
import sys

from bluesky.tests.conftest import RE

__copyright__ = 'Copyright (c) Brookhaven National Laboratory - 2020'


# By default, we don't use an external prefix
# and instead spawn IOCs in fixtures
EXTERNAL_PREFIX = None

# File pointer for outputting messages and test status.
# Defaults to stdout
OUTPUT_FP = sys.stdout


def write(text):
    """Wrapper around writing to the output file.
    """

    OUTPUT_FP.write(f'{text}\n')


def cleanup(error_code=0):
    """Function that ensures output file is closed as required, and exits
    """

    # And a newline at the end of program output
    OUTPUT_FP.write('')

    if OUTPUT_FP != sys.stdout:
        OUTPUT_FP.close()

    exit(error_code)


def validate_docker():
    """Function that checks if docker is installed

    Also ensures the simDetector IOC image is available

    Returns
    -------
    bool
        True if all requirements are met, false otherwise
    str
        Status/error message collected from docker
    """
    
    msg = None

    # Check if docker is installed by querying version    
    p = Popen(['docker', '--version'], stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    rc = p.returncode

    # If completed successfully, docker is installed
    if rc != 0:
        return False, err.decode('utf-8')
    else:
        msg = out.decode('utf-8')

    # Next check if epics simdetector IOC image is available
    p = Popen(['docker', 'image', 'ls'], stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    rc = p.returncode

    # If we completed the image list command, get image names
    if rc == 0:
        images = out.decode('utf-8').splitlines()[1:]
    
        img_found = False
        for line in images:

            # Check for the image we need
            if line.split()[0] == 'epics-ioc/simdetector':
                img_found = True
                break
        
        if not img_found:
            return False, 'Docker image for sim detector not found.'
    
        return True, msg
    else:
        return False, err.decode()
