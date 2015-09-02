#!/bin/sh

[ "$TERM" != 'xterm-256color' ] && export TERM='xterm-256color'
python -c 'from pykryptos.mengenlehreuhr import Mengenlehreuhr; Mengenlehreuhr().run()' "$@"
