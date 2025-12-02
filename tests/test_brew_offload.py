import functools
import unittest
import subprocess
import os
from pathlib import Path

from python_on_whales import DockerClient

from . import brew_offload

class Docker:
    DockerClient = DockerClient
    client = DockerClient(compose_files=["testenv/compose.yml"])

    @staticmethod
    def build():
        Docker.client.compose.build(cache=False)
    
    @staticmethod
    def with_docker(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                docker_client = Docker.client
                docker_client.compose.up(detach=True) # detach=True for watch command
                ret = func(docker_client=docker_client, *args, **kwargs)
            finally:
                docker_client.compose.down()
            return ret
        return wrapper


class BrewOffloadTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):    
        path = os.environ["PATH"]
        brew_path = Path("/home/linuxbrew/.linuxbrew/bin")
        brew_offload_path = Path("./bin")
        path = ":".join((str(brew_offload_path.absolute()), str(brew_path.absolute()), path))
        os.environ["PATH"] = path
        Docker.build()

    def test_brew_is_wrapped(self):
        result = subprocess.run(
            "source etc/brew-wrap; brew --version",
            shell=True, capture_output=True, text=True, executable="/bin/bash", timeout=2
        )
        self.assertEqual(result.stdout.splitlines()[0], "Your brew is wrapped by brew-offload")
        self.assertEqual(result.stderr, "")

    def test_argument_parse(self):
        args=["brew-offload", "wrapped", "list", "--help"]
        with self.subTest(args=args):
            namespace = brew_offload.arg_parse(*args)
            expected = {"offload": False, "original_brew_args": ["list", "--help"]}
            self.assertDictEqual(vars(namespace), expected)
        
        args=["brew-offload", "wrapped", "offload", "add", "example-formula"]
        with self.subTest(args=args):
            namespace = brew_offload.arg_parse(*args)
            expected = {"formula": "example-formula", "offload": True, "subcommand": "add"}
            self.assertDictEqual(vars(namespace), expected)
        
        args=["brew-offload", "remove", "example-formula"]
        with self.subTest(args=args):
            namespace = brew_offload.arg_parse(*args)
            expected = {"formula": "example-formula", "offload": True, "subcommand": "remove"}
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

    @Docker.with_docker
    def test_offload_function(self, docker_client: Docker.DockerClient):
        target_formula = "python@3.12"
        # to capture stdout and stderr, tty must be False
        docker_client.compose.execute("test", ["brew-offload", "add", target_formula], tty=False)
        brew_prefix = docker_client.compose.execute("test", ["brew", "--prefix"], tty=False)
        python_version = docker_client.compose.execute("test", [f"{brew_prefix}/opt/{target_formula}/bin/python3.12", "--version"], tty=False)
        self.assertListEqual(str(python_version).split(".")[:2], ["Python 3", "12"])
        is_symlink = docker_client.compose.execute("test", ["test", "-L", f"{brew_prefix}/Cellar/{target_formula}"], tty=False)
        # If execute brew doctor, occurs warning for Homebrew maintainers with non-zero return code.
        # docker_client.compose.execute("test", ["brew", "doctor"], tty=False)

    @Docker.with_docker
    def test_add_offloaded_formula(self, docker_client: Docker.DockerClient):
        target_formula = "python@3.12"
        docker_client.compose.execute("test", ["brew-offload", "add", target_formula], tty=False)
        stdout = docker_client.compose.execute("test", ["bash", "-c", f"brew-offload add {target_formula}; echo $?"], tty=False)
        return_code = int(str(stdout).splitlines()[-1])
        self.assertGreater(return_code, 0)

    @Docker.with_docker
    def test_config_file_does_not_exist(self, docker_client: Docker.DockerClient):
        docker_client.compose.execute("test", ["sudo", "rm", "-rf", "/etc/brew-offload"], tty=False)
        docker_client.compose.execute("test", ["brew-offload", "add", "python@3.12"], tty=False)

    @Docker.with_docker
    def test_move_offload_celllar(self, docker_client: Docker.DockerClient):
        old_offload_cellar = "/home/linuxbrew/.offload"
        new_offload_cellar = "/home/linuxbrew/testenv/new_cellar"
        docker_client.compose.execute("test", ["mkdir", "-p", new_offload_cellar], tty=False)
        docker_client.compose.execute("test", ["brew-offload", "add", "python@3.12"], tty=False)
        docker_client.compose.execute("test", ["brew-offload", "config", "offload_cellar", new_offload_cellar], tty=False)
        docker_client.compose.execute("test", ["python3.12", "--version"], tty=False)
