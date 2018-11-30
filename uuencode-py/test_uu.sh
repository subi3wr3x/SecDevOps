#!/bin/bash 

### Simple Tester / Wrapper ###

set -ue

UUFILE=$1
HELLOFILE="${UUFILE}".hello

sha256sum $UUFILE
./uu2hello.py $UUFILE
./hello2uu.py $HELLOFILE
sha256sum "$HELLOFILE".uue
diff $HELLOFILE $UUFILE
