import subprocess
import time
import os
import gevent
from config.services import launcher as launcher_config
from gevent import monkey
from build_python_path import process_dir


from services.service_base import SharedService

ready_processes = []

# This tiny BJsonRPC server, which receives notification from processes when
# they're ready.
class LauncherInfo(SharedService):
    config = launcher_config
    # Methods your service export.
    def _setup(self):
        pass

    def process_ready(self, pid):
        ready_processes.append(pid)


def dependent_processes_ready(process):
    for p in process.depends_on:
        if not p.pid in ready_processes:
            return False
    return True


def run_processes():
    executed_processes = []
    for process in processes:
        while(not dependent_processes_ready(process)):
            gevent.sleep(0.5)
        executed_processes.append(subprocess.Popen([process.command, process.params]))


if __name__ == '__main__':
    os.environ['PYXIS_ROOT'] = os.getcwd()

    from config.processes import processes
    pythonpath_dirs = process_dir(os.getcwd())
    pythonpath_dirs.append('%s/webui' %os.environ['PYXIS_ROOT'])
    os.environ['PYTHONPATH'] = ':'.join(pythonpath_dirs)
    monkey.patch_all()
    threads = [LauncherInfo.start()]
    run_processes()
    gevent.joinall(threads)
