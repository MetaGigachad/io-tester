#!/usr/bin/env python3

import subprocess
from argparse import ArgumentParser, Namespace, SUPPRESS
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import PosixPath

from termcolor import colored


class AutoName(Enum):
    def _generate_next_value_(name: str, *_):
        return name


class CompType(AutoName):
    EXACT = auto()
    NO_NEW_LINE = auto()
    NO_MULTIPLE_SPACES = auto()
    NO_ALL = auto()


@dataclass
class Test:
    name: str = ""
    input: str = ""
    output: str = ""


class TestFile:
    def __init__(self, path: PosixPath) -> None:
        self.path: PosixPath = path
        self.tests: list[Test] = []

        self._load_file()

    def _load_file(self):
        with open(self.path) as file:
            source = file.read().splitlines(keepends=True)

            is_in = None
            is_unused = False
            test = Test()

            for line in source:
                match line.removesuffix("\n").split():
                    case ["$test", test_name, "in"]:
                        test = Test(test_name)
                        is_in = True
                        is_unused = False
                    case ["$unused", test_name, "in"]:
                        test = Test(test_name)
                        is_in = True
                        is_unused = True
                    case ["$out"]:
                        is_in = False
                    case ["$end"]:
                        if not is_unused:
                            self.tests.append(test)
                        test = Test()
                        is_in = None
                    case ["#", *_]:
                        pass
                    case []:
                        if is_in is not None:
                            if is_in:
                                test.input += line
                            else:
                                test.output += line
                    case _:
                        if is_in is None:
                            raise RuntimeError(
                                "Test file syntax error: arbitrary text outside test data"
                            )

                        if is_in:
                            test.input += line
                        else:
                            test.output += line


def parse_args() -> Namespace:
    arg_parser = ArgumentParser()

    arg_parser.add_argument("executable", type=PosixPath,
                            help="path to executable to run tests on")
    arg_parser.add_argument("test_file", type=PosixPath, default=SUPPRESS,
                            help="path to file with test data (.iotest preferred)")
    arg_parser.add_argument(
        "--comp",
        "-c",
        type=CompType,
        choices=list(CompType),
        default=CompType.NO_NEW_LINE,
        help="comparator type for outputs: EXACT, NO_NEW_LINE, NO_MULTIPLE_SPACES, NO_ALL"
    )

    args = arg_parser.parse_args()

    if not hasattr(args, "test_file"):
        args.test_file = PosixPath(f"{args.executable}.iotest")

    if not args.executable.is_file():
        raise RuntimeError("executable doesn't exist")
    if not args.test_file.is_file():
        raise RuntimeError("test_file doesn't exist")

    return arg_parser.parse_args()


def main():
    args = parse_args()
    test_file = TestFile(args.test_file)

    print(f"Testing {args.executable} ... \n")

    for test in test_file.tests:
        print(f"Test {test.name}", end="\r")

        with open(".temp", "w") as tmp:
            tmp.write(test.input)

        run_result = subprocess.run(
            f"cat .temp | {args.executable.absolute()}",
            shell=True,
            text=True,
            check=True,
            stdout=subprocess.PIPE,
        )
        subprocess.run("rm .temp", shell=True, text=True, check=True)

        test_result = False

        filter_char = lambda text, char: " ".join(list(filter("".__ne__, text.split(char))))

        match args.comp:
            case CompType.EXACT:
                test_result = run_result.stdout == test.output
            case CompType.NO_NEW_LINE:
                test_result = filter_char(run_result.stdout, "\n") == filter_char(test.output, "\n")
            case CompType.NO_MULTIPLE_SPACES:
                test_result = filter_char(run_result.stdout, " ") == filter_char(test.output, " ")
            case CompType.NO_ALL:
                preprocess = lambda text: filter_char(filter_char(text, "\n"), " ")
                test_result = preprocess(run_result.stdout) == preprocess(test.output)

        if test_result:
            print(colored(f"Test {test.name}", "green"))
        else:
            print(colored(f"Test {test.name}", "red"))
            print(
                colored(f"\nTest output:", attrs=["bold"]),
                f"\n{test.output}",
                colored(f"\n{args.executable} output:", attrs=["bold"]),
                f"\n{run_result.stdout}\n",
            )


if __name__ == "__main__":
    main()
    try:
        print()
    except RuntimeError as err:
        print(*err.args)
