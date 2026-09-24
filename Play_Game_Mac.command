#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
if [ -d "$DIR/League of Rockets.app" ]; then
    open "$DIR/League of Rockets.app"
else
    open "$DIR/index.html"
fi
