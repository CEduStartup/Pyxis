"""This module provides functionality which allows to handle UNIX signal.
"""

import signal

def install_signal_handlers(config):
    """Install new signal handlers according to the given configuration.

    :Parameters:
        - `config`: dict of the following structure ::

          {
              'sig_name': The name of the signal from `signal` module e.g.:
                          signal.SIGHUP.
                    {
                        'handler': callable object which accepts 2 arguments:
                                   signal name and current stack frame object.
                        'keep_old_handler': bool, if `True` than old handler
                                            will be preserved and called after
                                            the new `handler`.
                    }
          }
    """
    for sig in config:
        new_handler = config[sig]['handler']
        old_handler = None
        keep_old_handler = config[sig]['keep_old_handler']

        if keep_old_handler:
            old_handler = signal.getsignal(sig)

        signal.signal(sig, _get_signal_handler(handler=new_handler,
                                               old_handler=old_handler))

def _get_signal_handler(handler, old_handler=None):
    """Return a callable object (signal handler).

    :Parameters:
        - `handler`: callable object. New signal handler.
        - `old_handler`: `None` or callable object. Old signal handler. If not
          `None` than it will be called after new signal handler.

    :Return:
        - `callable`: callable object as expected by `signal.signal()`.
    """

    def _handle_signal(sig_name, stack_frame):
        """New signal handler.
        """
        handler(sig_name, stack_frame)
        if old_handler is not None:
            old_handler(sig_name, stack_frame)

    return _handle_signal

