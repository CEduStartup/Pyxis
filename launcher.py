## Run Pyxis.
##
## This program uses configuration from config/processes.py
import argparse
import gevent
import os
import subprocess
import time
from build_python_path import process_dir
from config.services import launcher as launcher_config
from gevent import monkey
from services.service_base import SharedService


ready_processes = []


# This tiny BJsonRPC server, which receives notification from processes when
# they're ready. We need, because we have dependent processes - for example,
# Collector reuires shared services and logger.
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


def run_processes(debug=0):
    threads = []
    executed_processes = []
    for process in processes:
        while(not dependent_processes_ready(process)):
            gevent.sleep(0.5)
        process.set_debug(debug)
        cmd = [process.command]
        if isinstance(process.params, (list, tuple)):
            cmd.extend(process.params)
        else:
            cmd.append(process.params)
        executed_processes.append(subprocess.Popen(cmd, cwd=process.cwd))
        #threads.append(gevent.spawn(executed_processes[-1].wait))
    return threads


if __name__ == '__main__':
    os.environ['PYXIS_ROOT'] = os.getcwd()

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_const', const=1,
                        help='run system in debug mode')
    args = parser.parse_args()
    debug = args.debug or 0

    from config.processes import processes
    pythonpath_dirs = process_dir(os.getcwd())
    pythonpath_dirs.append('%s/webui' %os.environ['PYXIS_ROOT'])
    os.environ['PYTHONPATH'] = ':'.join(pythonpath_dirs)
    monkey.patch_all()
    threads = [LauncherInfo.start()] + run_processes(debug)
    gevent.joinall(threads)
