#!/usr/bin/env python
import os
import sys

def process_dir(dir_name):
    """Recursively walks through directory `dir_name` and looks for .py files.

    :Return:
        - list of strings to be added to `sys.path`
    """
    result = []

    def add_dirs(directory):
        if isinstance(directory, str):
            if not directory in result:
                result.append(directory)

        elif isinstance(directory, (list, tuple)):
            for d in directory:
                add_dirs(d)

    try:
        files = os.listdir(dir_name)
    except OSError, e:
        sys.stderr.write(str(e)+'\n')

    # Do not add directory to the PYTHONPATH in case when it's contain
    # `SKIP_AUTOPATH` file.
    if 'SKIP_AUTOPATH' in files:
        return

    # Do not add directory if it's contain __init__.py, but make sure that
    # parent dir is present in path.
    if '__init__.py' in files:
        if dir_name.endswith('/'):
            dir_name = dir_name[:-1]
        parent = os.path.dirname(dir_name)
        add_dirs(parent)
        return

    for f in files:
        path_item = os.path.join(dir_name, f)
        try:
            is_dir = os.path.isdir(path_item)
        except OSError, e:
            sys.stderr.write(str(e)+'\n')
            continue

        if is_dir:
            add_dirs(process_dir(path_item))

        elif f.endswith('.py'):
            add_dirs(dir_name)

    return result

path = process_dir(os.getcwd())

if __name__ == '__main__':
    print ':'.join(path)

else:
    sys.path = path + sys.path


