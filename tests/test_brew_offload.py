import functools
import fcntl
import json
import multiprocessing
import unittest
import subprocess
import time
import os
from pathlib import Path
from sys import version_info

from dotenv import load_dotenv
from python_on_whales import DockerClient

from . import brew_offload


def _run_brew_offload_add(env: dict[str, str], formula: str) -> int:
    os.environ.clear()
    os.environ.update(env)
    args = ["brew-offload", "add", formula]
    bf = brew_offload.BrewOffload(args)
    return bf.execute()

def _hold_config_lock(config_path: str, hold_seconds: float) -> int:
    with open(config_path, "a") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        time.sleep(hold_seconds)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    return 0

class Docker:
    client = DockerClient(compose_files=["testenv/compose.yml"])
    BREW_TEMPLATE_DIR = Path("placeholder")
    class TestEnv:
        def __init__(self, func_name: str):
            self.env = os.environ.copy()
            self.brew_directory = Path(self.env["BREW_TEMPLATE_DIR"]).parent / f"brew_{func_name}"
            self.env["PATH"] = f"{self.brew_directory}/brew/bin:{self.env['PATH']}"

        def run(self, command: str | list[str], *, shell: bool=False, check: bool=False) -> str:
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
            brew_directory = cls.BREW_TEMPLATE_DIR.parent / f"brew_{func.__name__}"
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
            f"source {wrapper} && brew --version",
            shell=True, capture_output=True, check=True, text=True, executable="/bin/bash", timeout=2,
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
        stdout = test_env.run("brew-offload add jq 2>&1", shell=True, check=True)
        self.assertEqual(stdout, "")

    @Docker.with_docker
    def test_move_offload_celllar(self, test_env: Docker.TestEnv):
        old_offload_cellar = test_env.brew_directory / "old_offload"
        new_offload_cellar = test_env.brew_directory / "new_offload"
        old_offload_cellar.mkdir()
        new_offload_cellar.mkdir()
        run = test_env.run
        run(["brew-offload", "config", "offload_cellar", str(old_offload_cellar)], shell=True, check=True)
        run(["brew-offload", "add", "jq"], shell=True, check=True)
        run(["brew-offload", "config", "offload_cellar", str(new_offload_cellar)], shell=True, check=True)
        run(["jq", "--version"], shell=True, check=True)
        cellar = run(["brew", "--cellar"], shell=True, check=True).strip()
        print(f"cellar: {cellar}")
        run(f"test -L {cellar}/jq", check=True, shell=True)

    @Docker.with_docker
    def test_move_offload_celllar_from_default(self, test_env: Docker.TestEnv):
        new_offload_cellar = test_env.brew_directory / "new_offload"
        run = test_env.run
        run(["brew-offload", "add", "jq"], shell=True, check=True)
        run(["mkdir", str(new_offload_cellar)], shell=True, check=True)
        run(["brew-offload", "config", "offload_cellar", str(new_offload_cellar)], shell=True, check=True)
        cellar = run(["brew", "--cellar"], shell=True, check=True).strip()
        run(f"test -L {cellar}/jq", check=True, shell=True)

    @Docker.with_docker
    def test_exclusive_control(self, test_env: Docker.TestEnv):
        try:
            formula = "test-formula"
            config_path = test_env.brew_directory / "brew" / "etc" / "brew-offload" / "config.json"

            lock_holder = multiprocessing.Process(
                target=_hold_config_lock,
                args=(str(config_path), 15),
            )
            lock_holder.start()
            time.sleep(0.5)

            env = test_env.env.copy()
            env["PYTHONPATH"] = "/workspaces/homebrew-offload/tests"
            add_process = multiprocessing.Process(
                target=_run_brew_offload_add,
                args=(env, formula),
            )
            add_process.start()

            add_process.join(timeout=20)
            lock_holder.join(timeout=20)

            self.assertEqual(add_process.exitcode, 1)
            self.assertEqual(lock_holder.exitcode, 0)

            with open(config_path, "r") as f:
                config = json.load(f)
            self.assertNotIn(formula, config["offloaded_formulae"])
        finally:
            pass
