# Xournal++

[Xournal++](https://xournalpp.github.io/) is a great open-source multi-platform application for taking notes with a drawing tablet.
For scripts related to the tablet itself, please see the [Wacom folder](../wacom) of this repository.

### Config synchronization
These instructions enable the synchronization of Xournal++ settings using a Git repository.

``` bash
# This will wipe your existing configs.
rm -r "${HOME}/.config/xournalpp"
# Replace the repository path with your own.
ln -s "${HOME}/Git/linux-scripts/xournalpp" "${HOME}/.config/xournalpp"
```
