#!/bin/bash 

### Simple Tester / Wrapper ###

set -ue

FILE=$1
sha256sum $FILE
UUFILE="${FILE}".uue
uuencode $FILE $FILE > $UUFILE
sha256sum $UUFILE

HELLOFILE="${UUFILE}".hello
./uu2hello.py $UUFILE
UUHELLOFILE="${UUFILE}".hello.uue
./hello2uu.py $HELLOFILE
sha256sum $UUHELLOFILE 
diff $UUFILE $UUHELLOFILE
