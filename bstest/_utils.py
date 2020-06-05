import os
import subprocess
import sys
import logging



@contextmanager
def softioc(prefix, ioc_path, additional_args=None,
            macros=None, env=None):
    '''[context manager] Start a soft IOC on-demand
    Parameters
    ----------
    prefix : str
        The prefix for the test IOC
    ioc_path : os.pathlike
        the path to the IOC st.cmd script
    additional_args : list
        List of additional args to pass to softIoc
    macros : dict
        Dictionary of key to value
    env : dict
        Environment variables to pass
    Yields
    ------
    proc : subprocess.Process
    '''

    if additional_args is None:
        additional_args = []

    if macros is None:
        macros = dict(P=prefix)

    proc_env = os.environ.copy()
    if env is not None:
        proc_env.update(**env)

    logger.debug('soft ioc environment is:')
    for key, val in sorted(proc_env.items()):
        if not key.startswith('_'):
            logger.debug('%s = %r', key, val)

    # if 'EPICS_' not in proc_env:

    macros = ','.join('{}={}'.format(k, v) for k, v in macros.items())

    popen_args = [executable,
                  '-m', macros]

    if sys.platform == 'win32':
        si = subprocess.STARTUPINFO()
        si.dwFlags = (subprocess.STARTF_USESTDHANDLES |
                      subprocess.CREATE_NEW_PROCESS_GROUP)
        os_kwargs = dict(startupinfo=si)
        executable = 'st.cmd'
    else:
        os_kwargs = {}
        executable = './st.cmd'

    cwd = os.getcwd()
    os.chdir(ioc_path)

    proc = subprocess.Popen(popen_args + additional_args, env=proc_env,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            **os_kwargs)

    os.chdir(cwd)

    try:
        yield proc
    finally:
        proc.kill()
        proc.wait()




class IocHandler:
    '''Benchmarking helper class
    Runs multiple IOCs and handles their cleanup.
    '''

    def __init__(self, logger=None):
        self.logger = (logger if logger is not None
                       else globals()['logger'])
        self._cms = []
        self._softioc_processes = []

    def setup_ioc(self, *, db_text, max_array_bytes=16384, env_vars=None,
                  **kwargs):
        if env_vars is None:
            env_vars = {}

        # NOTE: have to increase EPICS_CA_MAX_ARRAY_BYTES if NELM >= 4096
        #       (remember default is 16384 bytes / sizeof(int32) = 4096)
        env = dict(EPICS_CA_MAX_ARRAY_BYTES=str(max_array_bytes))
        env.update(**env_vars)

        cm = softioc(db_text=db_text, env=env, **kwargs)
        self._cms.append(cm)
        self._softioc_processes.append(cm.__enter__())
        self.logger.debug('Starting IOC with max_array_bytes=%s '
                          'env vars: %r database: %r', max_array_bytes,
                          env_vars, db_text)
        return cm

    @property
    def processes(self):
        return list(self._softioc_processes)

    def teardown(self):
        for i, cm in enumerate(self._cms[:]):
            self.logger.debug('Tearing down soft IOC context manager #%d', i)
            cm.__exit__(None, None, None)
            self._cms.remove(cm)

        for i, proc in enumerate(self._softioc_processes[:]):
            self.logger.debug('Killing soft IOC process #%d', i)
            proc.kill()
            self.logger.debug('Waiting for soft IOC process #%d', i)
            proc.wait()
            self._softioc_processes.remove(proc)

        self.logger.debug('IOC teardown complete')

    def wait(self):
        for i, proc in enumerate(self._softioc_processes[:]):
            self.logger.debug('Waiting for soft IOC process #%d', i)
            proc.wait()

        self.logger.debug('Waiting complete')
