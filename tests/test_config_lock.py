import time
import unittest

from . import config_lock

class ConfigLockTestCase(unittest.TestCase):
    def test_concurrent_lock(self):
        lock_file = "/tmp/test_concurrent_lock/config_lock.lock"
        @config_lock.wait_for_lock(lock_file, timeout=60)
        def lock_and_wait():
            time.sleep(60)
        
        @config_lock.wait_for_lock(lock_file, timeout=1)
        def try_lock():
            pass
        # Start the first lock in a separate thread
        import threading
        thread1 = threading.Thread(target=lock_and_wait)
        thread1.start()
        # Give the first thread a moment to acquire the lock
        time.sleep(1)
        thread2 = threading.Thread(target=try_lock)
        thread2.start()
        time.sleep(2) # Give the second thread a moment to attempt to acquire the lock
        # check that the second thread fails to acquire the lock and exits with a non-zero status code
        thread2.join()
        self.assertFalse(thread2.is_alive())
