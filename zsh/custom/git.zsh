#!/usr/bin/env zsh

git-pull() {
  # Pull all Git repositories in ~/Git and ~/git in parallel.
  # Arguments are passed to the script, e.g. "git-pull -j 1" for sequential pulls.
  python3 "${HOME}/Git/linux-scripts/git/pull.py" "${@}"
}
