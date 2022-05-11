from dataclasses import dataclass
from pathlib import Path

import typer
from rich import print as rprint
from rich.progress import Progress
from github.PullRequest import PullRequest

from voider import file_sieve, package_sieve
from voider.github import github_login


@dataclass
class TestCase:
    name: str
    pr_number: int
    expected_labels: list[str]
    expect_mismatch: bool


def read_token() -> str:
    with Path("./tokenfile").open("r") as tokenfile:
        return tokenfile.readline().strip()


def login():
    token = read_token()
    return github_login(token, "void-linux/void-packages")


def parse_tests(file: Path) -> list[TestCase]:
    cases = []
    with file.open("r") as f:
        # Dump the header
        _ = f.readline()
        for line in f.readlines():
            parts = line.strip().split("\t")
            if len(parts) != 4:
                raise Exception("Test cases should have 4 fields")
            pr_number = int(parts[0].split("/")[-1])
            name = parts[1]
            match parts[2].lower():
                case "true":
                    expect_mismatch = True
                case "false":
                    expect_mismatch = False
            expected_labels = parts[3].split(" ")
            cases += [TestCase(name, pr_number, expected_labels, expect_mismatch)]
    return cases


def run_test(test: TestCase, pr: PullRequest):
    files = list(pr.get_files())
    labels = [l.value for l in package_sieve(*file_sieve(files))]
    labels.sort(key=str.lower)
    expected_labels = sorted(test.expected_labels)
    isamatch = labels == expected_labels
    passed = isamatch ^ test.expect_mismatch

    status = "[green]PASS" if passed else "[red]FAIL"
    rprint(f"{status}\t[magenta]{test.pr_number}\t[bold cyan]{test.name}")
    if not passed:
        if test.expect_mismatch:
            rprint("\t[bold red]Labels unexpectedly matched!")
        else:
            rprint(f"\t[cyan]Expectation:\t[/]{expected_labels}")
            rprint(f"\t[cyan]Reality:\t[/]{labels}")
    return passed


cli = typer.Typer()

@cli.command()
def tests(filename: Path = typer.Argument(Path("./tests.tsv"))):
    """Runs the tests."""
    repo = login()
    tests = parse_tests(filename)
    with Progress() as progress:
        task = progress.add_task("[cyan]Running tests...", total=len(tests))
        for test in tests:
            pr = repo.get_pull(test.pr_number)
            run_test(test, pr)
            progress.advance(task)


@cli.command()
def labels(pr_number: int):
    """Print automatic labels for a PR."""
    print(pr_number)


if __name__ == "__main__":
    cli()
