import functools
import unittest
import subprocess
import sys
import os
from pathlib import Path
from sys import version_info

from dotenv import load_dotenv
from python_on_whales import DockerClient

from . import brew_offload

class Docker:
    client = DockerClient(compose_files=["testenv/compose.yml"])
    BREW_TEMPLATE_DIR = Path("placeholder")
    class TestEnv:
        def __init__(self, func_name: str):
            self.brew_directory = Path(f"/tmp/brew_{func_name}")
            self.env = os.environ.copy()
            # TODO : set path to temp brew directory, not to the template directory

        def execute(self, command: str | list[str]) -> str:
            result = subprocess.run(command, capture_output=True, text=True, executable="/bin/bash", timeout=60)
            return result.stdout

    @classmethod
    def build(cls):
        load_dotenv("./testenv/.env.test", override=True)
        brew_template_dir = os.getenv("BREW_TEMPLATE_DIR")
        if brew_template_dir is None:
            raise EnvironmentError("BREW_TEMPLATE_DIR environment variable is not set. Please set it in testenv/.env.test")
        cls.BREW_TEMPLATE_DIR = Path(brew_template_dir)
        subprocess.run(
            "./testenv/setup_brew_template.sh && brew --version && which brew",
            shell=True, check=True, text=True, executable="/bin/bash", timeout=600
        )
        build_args = {"PYTHON_VERSION": f"{version_info[0]}.{version_info[1]}"}
    
    @classmethod
    def with_docker(cls, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            brew_directory = Path(f"/tmp/brew_{func.__name__}")
            cls.BREW_TEMPLATE_DIR.copy(brew_directory)
            return func(test_env=cls.TestEnv(func.__name__), *args, **kwargs)
        return wrapper


class BrewOffloadTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Docker.build()

    def test_brew_is_wrapped(self):
        wrapper = Docker.BREW_TEMPLATE_DIR / "brew/etc/brew-offload/brew-wrap"
        result = subprocess.run(
            f"source {wrapper}; brew --version",
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
    def test_offload_function(self, test_env: Docker.TestEnv):
        target_formula = "jq"
        offload_cellar = test_env.brew_directory / "offload"
        test_env.execute(["brew-offload", "config", "offload_cellar", str(offload_cellar)])
        test_env.execute(["brew-offload", "add", target_formula])
        brew_prefix = test_env.execute(["brew", "--prefix"]).strip()
        python_version = test_env.execute(["bash", "-c", f"{brew_prefix}/opt/{target_formula}/bin/{target_formula} --version > /dev/null; echo $?"])
        self.assertEqual(int(python_version.strip()), 0)
        is_symlink = test_env.execute(["bash", "-c", f"test -L {brew_prefix}/Cellar/{target_formula}; echo $?"])
        self.assertEqual(is_symlink.strip(), "0")

    @Docker.with_docker
    def test_add_offloaded_formula(self, docker_client: Docker.DockerClient):
        target_formula = "python@3.12"
        offload_cellar = "/home/linuxbrew/.offload"
        # to capture stdout and stderr, tty must be False
        docker_client.compose.execute("test", ["brew-offload", "config", "offload_cellar", offload_cellar], tty=False)
        docker_client.compose.execute("test", ["brew-offload", "add", target_formula], tty=False)
        stdout = docker_client.compose.execute("test", ["bash", "-c", f"brew-offload add {target_formula}; echo $?"], tty=False)
        return_code = int(str(stdout).splitlines()[-1])
        self.assertGreater(return_code, 0)

    @Docker.with_docker
    def test_remove_offloaded_formula(self, docker_client: Docker.DockerClient):
        target_formula = "python@3.12"
        target_command = "python3.12"
        offload_cellar = "/home/linuxbrew/.offload"
        def execute(*command: str) -> str:
            return str(docker_client.compose.execute("test", list(command), tty=False))
        execute("brew-offload", "add", target_formula)
        execute("brew-offload", "remove", target_formula)
        execute(target_command, "--version")
        cellar = execute("brew", "--cellar").strip()
        stdout = execute("bash", "-c", f"test -L {cellar}/{target_formula}; echo $?")
        return_code = int(str(stdout).splitlines()[-1])
        self.assertGreater(return_code, 0)
        stdout = execute("bash", "-c", f"test -d {offload_cellar}/{target_formula}; echo $?")
        return_code = int(str(stdout).splitlines()[-1])
        self.assertGreater(return_code, 0)

        stdout = execute("bash", "-c", f"brew-offload remove {target_formula}; echo $?")
        return_code = int(str(stdout).splitlines()[-1])
        self.assertGreater(return_code, 0)

    @Docker.with_docker
    def test_config_file_does_not_exist(self, docker_client: Docker.DockerClient):
        offload_cellar = "/home/linuxbrew/.offload"
        docker_client.compose.execute("test", ["brew-offload", "config", "offload_cellar", offload_cellar], tty=False)
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
