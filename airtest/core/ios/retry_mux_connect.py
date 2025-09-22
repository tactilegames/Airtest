import functools
from time import sleep

from tidevice import ServiceError, MuxError, MuxServiceError


def retry_mux_connect(func):
    """
    Safe executes the wrapped function; in case the device connection is broken on function execute, it attempts to
    recover the connection and then retries executing the function.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        last_exception = None
        max_retries = 15
        delay_inbetween = 2

        for _ in range(max_retries):
            try:
                return func(*args, **kwargs)
            except (ServiceError, MuxError, MuxServiceError) as exception:
                last_exception = exception
                sleep(delay_inbetween)
                continue
        else:
            raise last_exception

    return wrapper