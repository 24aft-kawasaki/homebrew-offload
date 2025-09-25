import unittest
import subprocess
import os

class BrewOffloadTestCase(unittest.TestCase):
    def test_brew_is_wrapped(self):
        env = os.environ.copy()
        env["PS1"] = "$"
        completed = subprocess.run(
            "source ~/.bashrc && type brew && brew --version",
            text=True, capture_output=True, shell=True, executable="/bin/bash", env=env
        )
        print(completed.stdout)
        self.assertEqual(completed.stdout, "Your brew is wrapped by brew-offload")
