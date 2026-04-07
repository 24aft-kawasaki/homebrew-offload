import fcntl
import os
import time
import unittest

from multiprocessing import Process
from pathlib         import Path
from tempfile        import NamedTemporaryFile

from . import config_lock

def _hold_lock_for_seconds(path, seconds):
    with open(path, "a") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        time.sleep(seconds)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

class ConfigLockTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_file = NamedTemporaryFile(delete=False)
        self.lock_path = self.tmp_file.name
        # test doesn't need the file content, just the path, so we can close and delete it immediately
        self.tmp_file.close()
    
    def tearDown(self) -> None:
        lock_file = Path(self.lock_path)
        if lock_file.exists():
            os.remove(lock_file)
    
    def test_lock_success_when_free(self):
        with config_lock.wait_for_lock(self.lock_path, timeout=2) as lock:
            self.assertTrue(lock.writable())
    
    def test_lock_waits_and_succeeds(self):
        start = time.time()

        p_timeout = 2
        p = Process(target=_hold_lock_for_seconds, args=(self.lock_path, p_timeout))
        p.start()

        sleep_time = 0.5
        time.sleep(sleep_time)

        main_timeout = 5
        assert main_timeout > p_timeout
        with config_lock.wait_for_lock(self.lock_path, timeout=main_timeout):
            elapsed = time.time() - start
            self.assertGreaterEqual(elapsed, p_timeout)
            self.assertLess(elapsed, main_timeout)
        
        p.join()
    
    def test_lock_timeout_exits(self):
        p_timeout = 10
        p = Process(target=_hold_lock_for_seconds, args=(self.lock_path, p_timeout))
        p.start()

        time.sleep(0.5)

        main_timeout = 2
        assert main_timeout < p_timeout
        with self.assertRaises(SystemExit) as e:
            with config_lock.wait_for_lock(self.lock_path, timeout=main_timeout):
                pass
        
        self.assertEqual(e.exception.code, 1)
        p.terminate()
        p.join()

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
