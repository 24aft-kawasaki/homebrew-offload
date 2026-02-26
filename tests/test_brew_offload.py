import functools
import unittest
import subprocess
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
            self.env["PATH"] = f"{self.brew_directory}/brew/bin:{self.env['PATH']}"

        def run(self, command: str | list[str], shell: bool=False, *, check: bool=False) -> str:
            # どちらの型でもシェルを使うので、リストを文字列に変換
            if isinstance(command, list) and shell:
                command = " ".join(str(arg) for arg in command)
            result = subprocess.run(command, shell=shell, env=self.env, capture_output=True, check=check, text=True, executable="/bin/bash", timeout=60)
            return result.stdout

    @classmethod
    def build(cls, cache=False):
        load_dotenv("./testenv/.env.test", override=True)
        brew_template_dir = os.getenv("BREW_TEMPLATE_DIR")
        if brew_template_dir is None:
            raise EnvironmentError("BREW_TEMPLATE_DIR environment variable is not set. Please set it in testenv/.env.test")
        cls.BREW_TEMPLATE_DIR = Path(brew_template_dir)
        if cache:
            print("Using cached brew template directory, skipping setup script")
            return
        # clean any existing template so setup script can recreate it
        subprocess.run(f"rm -rf {brew_template_dir}", shell=True, check=False)
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
            cls.BREW_TEMPLATE_DIR.copy(brew_directory, preserve_metadata=True)
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
        # make sure offload cellar exists so config command succeeds
        offload_cellar.mkdir(parents=True, exist_ok=True)
        path = test_env.run("echo $PATH", shell=True, check=True)
        print(f"PATH: {path}")
        which_brew_offload = test_env.run("which brew-offload", shell=True)
        self.assertEqual(which_brew_offload.strip(), f"{test_env.brew_directory}/brew/bin/brew-offload")
        print(f"which brew-offload: {which_brew_offload}")
        test_env.run(f"brew-offload config offload_cellar {offload_cellar}", shell=True, check=True)
        test_env.run(f"brew-offload add {target_formula}", shell=True, check=True)
        brew_prefix = test_env.run(["brew", "--prefix"], shell=True).strip()
        print(f"brew prefix: {brew_prefix}")
        python_version = test_env.run(["bash", "-c", f"{brew_prefix}/opt/{target_formula}/bin/{target_formula} --version > /dev/null; echo $?"])
        self.assertEqual(int(python_version.strip()), 0)
        is_symlink = test_env.run(["bash", "-c", f"test -L {brew_prefix}/Cellar/{target_formula}; echo $?"])
        self.assertEqual(is_symlink.strip(), "0")

    @Docker.with_docker
    def test_add_offloaded_formula(self, test_env: Docker.TestEnv):
        target_formula = "jq"
        offload_cellar = test_env.brew_directory / "offload"
        offload_cellar.mkdir()
        test_env.run(["brew-offload", "config", "offload_cellar", str(offload_cellar)], shell=True, check=True)
        test_env.run(["brew-offload", "add", target_formula], shell=True, check=True)
        with self.assertRaises(subprocess.CalledProcessError):
            test_env.run(["brew-offload", "add", target_formula], shell=True, check=True)

    @Docker.with_docker
    def test_remove_offloaded_formula(self, test_env: Docker.TestEnv):
        target_formula = "jq"
        target_command = "jq"
        offload_cellar = test_env.brew_directory / "offload"
        offload_cellar.mkdir()
        def execute(*command: str) -> str:
            return test_env.run(list(command), shell=True, check=True)
        execute(f"brew-offload config offload_cellar {offload_cellar}")
        stdout = execute("brew-offload", "add",    target_formula, "2>&1", "||", "true")
        self.assertEqual(stdout, "")
        execute("brew-offload", "remove", target_formula)
        execute(target_command, "--version")
        cellar = execute("brew", "--cellar").strip()
        with self.assertRaises(subprocess.CalledProcessError):
            execute(f"test -L {cellar}/{target_formula}")
        with self.assertRaises(subprocess.CalledProcessError):
            execute(f"test -d {offload_cellar}/{target_formula}")
        with self.assertRaises(subprocess.CalledProcessError):
            execute(f"brew-offload remove {target_formula}")

    @Docker.with_docker
    def test_config_file_does_not_exist(self, test_env: Docker.TestEnv):
        offload_cellar = test_env.brew_directory / "offload"
        offload_cellar.mkdir()
        test_env.run(["brew-offload", "config", "offload_cellar", str(offload_cellar)], shell=True, check=True)
        test_env.run(["rm", "-rf", f"{test_env.brew_directory}/brew/etc/brew-offload/config.json"], shell=True, check=True)
        stdout = test_env.run("brew-offload add jq 2>&1", shell=True, check=False)
        self.assertEqual(stdout, "")

    @Docker.with_docker
    def test_move_offload_celllar(self, docker_client: Docker.DockerClient):
        old_offload_cellar = "/home/linuxbrew/.offload"
        new_offload_cellar = "/home/linuxbrew/testenv/new_cellar"
        docker_client.compose.execute("test", ["mkdir", "-p", new_offload_cellar], tty=False)
        docker_client.compose.execute("test", ["brew-offload", "add", "python@3.12"], tty=False)
        docker_client.compose.execute("test", ["brew-offload", "config", "offload_cellar", new_offload_cellar], tty=False)
        docker_client.compose.execute("test", ["python3.12", "--version"], tty=False)
