#!/usr/bin/env python3.12

import argparse
import sys
import subprocess

class BrewOffload:
    def __init__(self, *args):
        self._args = args
    
    def exec_brew(self):
        """execute brew"""
        subprocess.run(["brew"] + [*self._args])
    
    def exec_custom_offload(self):
        """Execute custom offload operations not provided by Homebrew.

        This method is intended for implementing additional tasks or custom logic
        that extend beyond the standard functionality of Homebrew."""
  
        pass
    
    def offlad(self):
        """offload formulae"""
        pass

def arg_parse(*args: list[str]):
    parser = argparse.ArgumentParser()
    
    parser.add_argument("wrapped")
    parser.add_argument("remainder", nargs=argparse.REMAINDER)
    namespace = parser.parse_args(args[1:])
    if namespace.wrapped == "wrapped":
        parser = argparse.ArgumentParser(prog="brew")
        parser.add_argument("offload")
        parser.add_argument("remainder", nargs=argparse.REMAINDER)
        namespace = parser.parse_args(namespace.remainder)
        if namespace.offload == "offload":
            parser = argparse.ArgumentParser(prog="brew offload")
        else:
            pass
    else:
        parser = argparse.ArgumentParser(prog="brew-offload")
        subparsers = parser.add_subparsers(title="subcommands")
        subparsers.add_parser("add")
        subparsers.add_parser("remove")
        namespace = parser.parse_args(args[1:])

    """
    if args[1] == "--wrapped":
        parser = argparse.ArgumentParser(prog="brew")
        parser.add_argument("subcommand")
        

        subparsers = parser.add_subparsers()
        offload_parser = subparsers.add_parser("offload")
        offload_parser.add_argument("subcommand")
        parser.print_usage()
        namespace = parser.parse_args(args[2:])
    else:
        parser = argparse.ArgumentParser(prog="brew-offload")
    """
    return namespace

def main() -> int:
    # parse args
    # if args[0] == "offload":
    #     BrewOffload(*args[1:]).offlad()
    # else:
    #    BrewOffload(*args).exec_brew()
    pass

if __name__ == "__main__":
    result = arg_parse("brew", "hoge")
    print(result)
    exit(main())