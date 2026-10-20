#!/usr/bin/env python3

"""Pull all Git repositories cloned directly in ~/Git and ~/git.

The pulls are run in parallel, but the output of each repository is printed
as a single block in alphabetical order.
Only fast-forward pulls are performed, so that no merge commits or rebases are created unattended.
"""

import argparse
import concurrent.futures
import dataclasses
import os
import pathlib
import subprocess
import sys
import typing as tp

DEFAULT_ROOTS = (pathlib.Path.home() / "Git", pathlib.Path.home() / "git")
# GitHub does not document a hard limit for Git operations,
# but too many simultaneous SSH connections can get throttled.
# A small pool gives most of the speedup without hammering the servers.
DEFAULT_JOBS = 8
DEFAULT_TIMEOUT = 300


@dataclasses.dataclass
class PullResult:
    repo: pathlib.Path
    returncode: int
    output: str


def find_repos(roots: tp.Iterable[pathlib.Path]) -> list[pathlib.Path]:
    """Find the Git repositories that are direct subdirectories of the given roots."""
    repos: dict[pathlib.Path, pathlib.Path] = {}
    for root in roots:
        if not root.is_dir():
            continue
        for path in root.iterdir():
            # Worktrees and submodules have a .git file instead of a directory.
            if path.is_dir() and not path.is_symlink() and (path / ".git").exists():
                # Deduplicate in case ~/Git and ~/git point to the same directory.
                repos.setdefault(path.resolve(), path)
    return sorted(repos.values(), key=lambda path: (path.name.lower(), str(path)))


def pull(repo: pathlib.Path, timeout: float = DEFAULT_TIMEOUT) -> PullResult:
    """Pull a single repository without allowing interactive prompts."""
    env = os.environ.copy()
    # Fail instead of waiting for a username or password that cannot be typed in parallel mode.
    env["GIT_TERMINAL_PROMPT"] = "0"
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo), "pull", "--ff-only"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            text=True,
            errors="replace",
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return PullResult(repo, 124, f"Timed out after {timeout} s.\n")
    except OSError as e:
        return PullResult(repo, 1, f"{e}\n")
    return PullResult(repo, proc.returncode, proc.stdout)


def print_result(result: PullResult, color: bool) -> None:
    bold, red, reset = ("\033[1m", "\033[31m", "\033[0m") if color else ("", "", "")
    status = "" if result.returncode == 0 else f" {red}(failed with code {result.returncode}){reset}"
    print(f"{bold}{result.repo}{reset}{status}")
    if result.output:
        print(result.output, end="" if result.output.endswith("\n") else "\n")
    print(flush=True)


def pull_all(
        repos: tp.Sequence[pathlib.Path],
        jobs: int = DEFAULT_JOBS,
        timeout: float = DEFAULT_TIMEOUT,
        color: bool = False) -> list[PullResult]:
    """Pull the repositories in parallel and print each result in order as soon as it is available."""
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(jobs, 1)) as executor:
        futures = [executor.submit(pull, repo, timeout) for repo in repos]
        for future in futures:
            result = future.result()
            print_result(result, color)
            results.append(result)
    return results


def main(argv: tp.Optional[tp.Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "-j", "--jobs", type=int, default=DEFAULT_JOBS,
        help=f"number of parallel pulls (default: {DEFAULT_JOBS}, use 1 for sequential)")
    parser.add_argument(
        "-t", "--timeout", type=float, default=DEFAULT_TIMEOUT,
        help=f"timeout for each pull in seconds (default: {DEFAULT_TIMEOUT})")
    parser.add_argument(
        "roots", nargs="*", type=pathlib.Path,
        help="directories containing the repositories (default: ~/Git and ~/git)")
    args = parser.parse_args(argv)

    repos = find_repos(args.roots or DEFAULT_ROOTS)
    if not repos:
        print("No Git repositories found.", file=sys.stderr)
        return 1
    color = sys.stdout.isatty() and "NO_COLOR" not in os.environ
    results = pull_all(repos, jobs=args.jobs, timeout=args.timeout, color=color)

    failed = [result for result in results if result.returncode != 0]
    print(f"Pulled {len(results) - len(failed)}/{len(results)} repositories successfully.")
    if failed:
        print("Failed:")
        for result in failed:
            print(f"  {result.repo}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
