import fcntl
import os
import time
import unittest

from pathlib import Path
from tempfile import NamedTemporaryFile

from . import config_lock

class ConfigLockTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_file = NamedTemporaryFile(delete=False)
        self.lock_path = self.tmp_file.name
    
    def tearDown(self) -> None:
        lock_file = Path(self.lock_path)
        if lock_file.exists():
            os.remove(lock_file)
    
    def test_decorated_function_execution(self):
        expect = "success"
        @config_lock.wait_for_lock(self.lock_path, timeout=5)
        def my_task():
            return expect
        
        self.assertEqual(my_task(), expect)
    
    def test_decorated_function_blocks_others(self):
        with open(self.lock_path, "a") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)

            @config_lock.wait_for_lock(self.lock_path, timeout=1)
            def blocked_task():
                pass
            
            with self.assertRaises(SystemExit) as e:
                blocked_task()
            
            self.assertEqual(e.exception.code, 1)

"""
    def _hold_lock_for_seconds(self, path, seconds):
        with open(path, "a") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            time.sleep(seconds)
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)

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
"""
