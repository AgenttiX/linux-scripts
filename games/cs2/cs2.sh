#!/bin/bash -a
# From:
# https://www.reddit.com/r/linux_gaming/comments/171ssnk/cs2_linux_customise_and_adjust_your_cs2sh_file/
# https://raw.githubusercontent.com/MichaelDeets/cs2.sh/master/cs2-example.sh

GAMEROOT=$(cd "${0%/*}" && echo $PWD)
UNAME=$(command -v uname)
export LD_LIBRARY_PATH="${GAMEROOT}"/bin/linuxsteamrt64:$LD_LIBRARY_PATH

USE_STEAM_RUNTIME=1
GAMEEXE=bin/linuxsteamrt64/cs2

ulimit -n 2048
ulimit -Ss 1024

cd "$GAMEROOT"

export ENABLE_PATHMATCH=1

# Run inside of the Steam runtime if necessary and allowed.
if [ "$STEAM_RUNTIME_ROOT" != "" ]; then
    # Already in the runtime.
    USE_STEAM_RUNTIME=0
fi
if [ "$STEAM_RUNTIME" = "0" ]; then
    # Runtime is explicitly disabled.
    USE_STEAM_RUNTIME=0
fi

if [ "$USE_STEAM_RUNTIME" = "1" ]; then
    STEAM_RUNTIME_PREFIX=/valve/steam-runtime/shell.sh
    if [ ! -f $STEAM_RUNTIME_PREFIX ]; then
        STEAM_RUNTIME_PREFIX=
    fi
    if [ "$STEAM_RUNTIME_PREFIX" != "" ]; then
        echo "Running with the Steam runtime SDK"
    fi
fi

export SDL_VIDEO_DRIVER=x11

STATUS=42
while [ $STATUS -eq 42 ]; do
	if [ "${GAME_DEBUGGER}" == "gdb" ] || [ "${GAME_DEBUGGER}" == "cgdb" ]; then
		ARGSFILE=$(mktemp $USER.cs2.gdb.XXXX)
		echo b main > "$ARGSFILE"

		# Set the LD_PRELOAD varname in the debugger, and unset the global version. This makes it so that
		#   gameoverlayrenderer.so and the other preload objects aren't loaded in our debugger's process.
		echo set env LD_PRELOAD=$LD_PRELOAD >> "$ARGSFILE"
		echo show env LD_PRELOAD >> "$ARGSFILE"
		echo set disable-randomization off >> "$ARGSFILE"
		unset LD_PRELOAD

		echo run $@ >> "$ARGSFILE"
		echo show args >> "$ARGSFILE"
		${GAME_DEBUGGER} "${GAMEROOT}"/${GAMEEXE} -x "$ARGSFILE"
		rm "$ARGSFILE"
	elif [ "${GAME_DEBUGGER}" == "lldb" ]; then
		${GAME_DEBUGGER} "${GAMEROOT}"/${GAMEEXE} -- $@
	else
		${STEAM_RUNTIME_PREFIX} ${GAME_DEBUGGER} "${GAMEROOT}"/${GAMEEXE} "$@"
	fi
	STATUS=$?
done
exit $STATUS
