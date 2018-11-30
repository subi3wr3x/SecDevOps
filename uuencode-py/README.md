#### uuencode-py
Encode and decode uuencoded file using a mapping of your choosing (pentest,etc).

#### Usage
```
./uu2hello.py UUENCODED_FILE.UUE (creates UUENCODED_FILE.UUE.hello
```

Send it somewhere...

```
./hello2uu.py UUENCODED_FILE.UUE.hello (creates UUENCODED_FILE.UUE)
```

#### Examples
Take a.uue file, convert it and then convert back using the included 'test_uu.sh'

```
$ ./test_uu.sh  test.text.tar.uue
d42390e88b8faeaa2e1732c57dc71ea8c5f240663ff43132999006148ebba048  test.text.tar.uue
d42390e88b8faeaa2e1732c57dc71ea8c5f240663ff43132999006148ebba048  test.text.tar.uue.hello.uue
```


