"""
lock the config file to prevent concurrent modifications
"""

import fcntl
import time
from contextlib import contextmanager

@contextmanager
def wait_for_lock(lock_path, timeout=10):
    start_time = time.time()

    with open(lock_path, "a") as lock:
        fd = lock.fileno()

        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break

            except BlockingIOError:
                if time.time() - start_time >= timeout:
                    exit(1)
                time.sleep(1)
    
    try:
        yield lock
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
                

def test_import() -> None:
    """Test that the config_lock module can be imported without errors."""
    pass
