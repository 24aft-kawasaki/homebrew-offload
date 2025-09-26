import unittest
import subprocess
import os
from pathlib import Path

class BrewOffloadTestCase(unittest.TestCase):
    def setUp(self):
        path = os.environ["PATH"]
        brew_path = Path("/home/linuxbrew/.linuxbrew/bin")
        brew_offload_path = Path("./bin/brew-offload")
        path = ":".join((str(brew_offload_path.absolute()), str(brew_path.absolute()), path))
        os.environ["PATH"] = path

    def test_brew_is_wrapped(self):
        result = subprocess.run(
            "source etc/brew-wrap; brew --version",
            shell=True, capture_output=True, text=True, executable="/bin/bash", timeout=2
        )
        self.assertEqual(result.stdout.splitlines()[0], "Your brew is wrapped by brew-offload")
