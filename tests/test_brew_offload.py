import unittest
import subprocess
import os
from pathlib import Path

from . import brew_offload

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

    def test_argument_parse(self):
        args=["brew-offload", "wrapped", "list", "--help"]
        with self.subTest(args=args):
            namespace = brew_offload.arg_parse(*args)
            expected = {"offload": False, "original_brew_args": ["list", "--help"]}
            self.assertDictEqual(vars(namespace), expected)
        
        args=["brew-offload", "wrapped", "offload", "add"]
        with self.subTest(args=args):
            namespace = brew_offload.arg_parse(*args)
            expected = {"offload": True, "subcommand": "add"}
            self.assertDictEqual(vars(namespace), expected)
        
        args=["brew-offload", "remove"]
        with self.subTest(args=args):
            namespace = brew_offload.arg_parse(*args)
            expected = {"offload": True, "subcommand": "remove"}
            self.assertDictEqual(vars(namespace), expected)

    def test_brew_offload_pass_through(self):
        args = ["brew-offload", "wrapped", "list"]
        with self.subTest(args=args):
            bf = brew_offload.BrewOffload(args)
            returncode = bf.execute_original_brew(bf.args.original_brew_args)
            self.assertEqual(returncode, 0)
        args = ["brew-offload", "wrapped", "info", "nonexistent-formula"]
        with self.subTest(args=args):
            bf = brew_offload.BrewOffload(args)
            returncode = bf.execute_original_brew(bf.args.original_brew_args)
            self.assertNotEqual(returncode, 0)

    def test_offload_function(self):
        formula = "python@3.12"
        bf = brew_offload.BrewOffload(["brew-offload", "wrapped", "list"])
        self.assertEqual(bf.offload(), 0)
        cellar_path = bf.brew_cellar_path
        self.assertTrue((cellar_path / formula).is_symlink())
        brew_prefix = subprocess.run(
            ["brew", "--prefix"],
            capture_output=True, text=True, check=True
        ).stdout.strip()
        completed = subprocess.run(
            [brew_prefix + "/opt/python@3.12/bin/python3.12", "--version"],
            capture_output=True, text=True, check=True
        )
        self.assertEqual(completed.returncode, 0)
