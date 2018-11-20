#!/bin/bash 

### Simple Tester / Wrapper ###

set -ue

UUFILE=$1
HELLOFILE="${UUFILE}".hello

./uu2hello.py $UUFILE
./hello2uu.py $HELLOFILE
diff $UUFILE "${HELLOFILE}".uue
