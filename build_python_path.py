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

if __name__ == '__main__':
    help_msg = """\
Usage:
export PYTHONPATH=`python build_python_path.py [path_to_dir]`:$PYTHONPATH

Please start this program without arguments to build PYTHONPATH for all subdirs
of Pyxis directory (usually this is what you need). Otherwise if you need to
build PYTHONPATH for separate directory then specify its absolute path as a
first argument (you also can specify relative path starting from directory
where this script is located).
"""

    if len(sys.argv) > 2:
        print help_msg
        sys.exit(-1)

    elif len(sys.argv) == 2:
        dir_name = sys.argv[1]

        if dir_name == '-h' or dir_name == '--help':
            print help_msg
            sys.exit()

        if not dir_name.startswith('/'):
            dir_name = os.path.abspath(dir_name)
    else:
        dir_name = os.getcwd()

    path = process_dir(dir_name)
    print ':'.join(path)



