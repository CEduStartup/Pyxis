## Run Pyxis.
##
## This program uses configuration from config/processes.py
import gevent
from gevent import monkey
monkey.patch_all()
import subprocess
import os
from config.mq import queue_host, queue_port
from build_python_path import process_dir
from shared.events.GEventDispatcher import GEventDispatcher
from shared.events.Event import ServiceChangedStateEvent, LAUNCHER_TUBE


# Some processes have to inform Launcher that they're started and ready.
# For example, collector depends on shared services. Dependent processes are
# specified in process configuration (config/processes.py).
ready_processes = []

def on_service_state_event(event):
    """This happens when some processes tells Launcher that it is ready."""
    if event.state == 'started':
        ready_processes.append(event.service_id)


# Waiting for "Service Started" events.
receiver = GEventDispatcher(queue_host, queue_port, (LAUNCHER_TUBE,))
receiver.subscribe((ServiceChangedStateEvent,), on_service_state_event)
event_thread = gevent.spawn(receiver.dispatch)


def dependent_processes_ready(process):
    """Checks if all dependent processes are ready.

    :Parameters:
        `process`: process instance (from config/processes.py)
    """
    for p in process.depends_on:
        if not p.pid in ready_processes:
            return False
    return True


def run_processes():
    executed_processes = []
    for process in processes:
        while(not dependent_processes_ready(process)):
            gevent.sleep(0.5)
        cmd = [process.command]
        if isinstance(process.params, (list, tuple)):
            cmd.extend(process.params)
        else:
            cmd.append(process.params)
        subprocess.Popen(cmd, cwd=process.cwd)


if __name__ == '__main__':
    os.environ['PYXIS_ROOT'] = os.getcwd()
    from config.processes import processes

    pythonpath_dirs = process_dir(os.getcwd())
    pythonpath_dirs.append('%s/webui' %os.environ['PYXIS_ROOT'])
    os.environ['PYTHONPATH'] = ':'.join(pythonpath_dirs)

    run_processes()
    while True:
        gevent.sleep(0.01)
